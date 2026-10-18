"""A+ Core 2 4.6 (incident handling, licensing, regulated data, policy) — ITSUP 12.2; 4.7 (communication and
professionalism) — ITSUP 1.4.  Round 2 of pass 11."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG_IR = figure(
    'fig-c-incident', 'When you find prohibited content or evidence of an incident',
    ['Stop:\ndo not browse further,\ndo not delete', 'Report:\ninform management;\nthey involve law enforcement', 'Preserve:\nforensic copy of the drive,\nwrite blocker, hash', 'Record:\nchain of custody\nand incident documentation'],
    'Four boxes. When a technician finds prohibited content or signs of an incident, they stop: they do not keep browsing, copy or '
    'delete anything. They report to management through the proper channel; management decides whether to inform law enforcement. '
    'Evidence is preserved by a qualified person who makes a forensic copy of the drive through a write blocker and records a hash, '
    'collecting the most volatile data first. Every hand-over is logged in the chain of custody, and the incident is documented.',
    'Stop, report, preserve, record. The technician who found it is a witness, not the investigator.', cols=4)

HTML_POL = f'''
<p>A+ Core 2 4.6 covers how to handle prohibited content and incidents, and why licensing, regulated data and policies matter.</p>
<h4>Incident response basics</h4>
<ul>
<li><strong>Inform management and, through them, law enforcement</strong> when the policy or law requires it.</li>
<li><strong>Chain of custody</strong> — a record of who held the evidence, when and why, from collection to court; a gap can make evidence unusable.</li>
<li><strong>Copy of drive</strong> — preserve <em>data integrity</em> by imaging through a write blocker and recording a hash of the original and the copy (NIST SP 800-86).</li>
<li><strong>Order of volatility</strong> — collect what disappears first: CPU registers and cache, then memory, routing and process tables,
then temporary files, then disk, then remote logs and archives (RFC 3227).</li>
<li><strong>Documentation of the incident</strong> — what was seen, when, by whom and what was done.</li>
</ul>
<h4>Licensing</h4>
<ul>
<li><strong>Valid licences</strong> for every install; <strong>DRM</strong> (digital rights management) enforces use rules technically; the
<strong>EULA</strong> (end-user licence agreement) is the legal terms.</li>
<li><strong>Perpetual</strong> licence (pay once, use that version) vs. <strong>subscription</strong> (pay per period, stops when payment stops).</li>
<li><strong>Personal use vs. corporate use</strong> — a “free for personal use” or home licence usually does not allow business use.</li>
<li><strong>Open-source</strong> licences (OSI-approved, such as GPL, MIT, Apache) allow use, change and sharing, but carry conditions such as keeping notices.</li>
</ul>
<h4>Regulated data and policies</h4>
<ul>
<li><strong>Credit card data</strong> — PCI DSS rules on storing and handling cardholder data.</li>
<li><strong>Government-issued information</strong> (passport, driver’s licence, national ID numbers) and other <strong>PII</strong> (personally identifiable information).</li>
<li><strong>Healthcare data</strong> — protected health information under HIPAA in the U.S.</li>
<li><strong>Data retention requirements</strong> — keep records for the legally required period, then dispose of them securely.</li>
<li><strong>NDA / MNDA</strong> — non-disclosure agreement (mutual when both parties share secrets).</li>
<li><strong>AUP</strong> (acceptable use policy) and <strong>splash screens</strong> / logon banners that remind users of the policy and monitoring before sign-in.</li>
</ul>
{_FIG_IR}
{worked('a repair that turned into an incident', '''<ol>
<li>While recovering files, a technician sees images that appear to be prohibited content.</li>
<li>They stop, close nothing further, do not copy or delete, and tell their manager straight away.</li>
<li>The manager follows policy and contacts law enforcement; the laptop is bagged, labelled and signed for on a chain-of-custody form.</li>
<li>The technician writes down what they saw, when, and every action taken; they do not discuss it with the customer or colleagues.</li></ol>''')}
{scenario('the “free” PDF editor', '''<p>A department installs a PDF editor whose licence says “free for personal, non-commercial use”. A software audit flags
40 installs. The service desk explains that the EULA does not cover business use, removes the copies, and buys a subscription
licence. A new rule is added to the AUP: only software from the approved catalogue, which records each licence type.</p>''')}
{cfu(('What is chain of custody?', 'A record of everyone who handled the evidence, when and why.'),
     ('What is collected first under the order of volatility?', 'The most volatile data, such as CPU cache and memory, before disk.'),
     ('What is the difference between a perpetual and a subscription licence?', 'Perpetual: pay once for a version; subscription: pay each period while you use it.'))}
'''

HTML_PRO = f'''
<p>A+ Core 2 4.7 lists the communication and professional behaviours expected of a technician.</p>
<ul>
<li><strong>Professional appearance and attire</strong> — match the site: formal for an office visit, business casual or the company dress code otherwise.</li>
<li><strong>Use proper language</strong> — avoid jargon, acronyms and slang; explain in plain language.</li>
<li><strong>Maintain a positive attitude</strong> and project confidence.</li>
<li><strong>Actively listen</strong> and take notes; do not interrupt. <strong>Be culturally sensitive</strong> — use proper titles and respect differences.</li>
<li><strong>Be on time</strong>; if you will be late, contact the customer before the agreed time.</li>
<li><strong>Avoid distractions</strong> — no personal calls, texting or social media; no talking to co-workers about unrelated things; no personal interruptions.</li>
<li><strong>Dealing with a difficult customer or situation</strong> — do not argue or be defensive, do not minimise the problem, avoid being judgemental;
<strong>clarify</strong> by asking open-ended questions and restating the issue to confirm understanding; do not disclose experience on social media.</li>
<li><strong>Set and meet expectations</strong> — agree a timeline and keep the customer updated; offer repair or replacement options where they apply;
provide proper documentation of the services; follow up afterwards to confirm satisfaction.</li>
<li><strong>Deal appropriately with confidential and private materials</strong> on computers, desks, printers and phones — do not look, copy or share.</li>
</ul>
{worked('a call with an angry user', '''<ol>
<li>Let them finish; take notes (active listening). Do not interrupt or argue.</li>
<li>Restate: “So since this morning your laptop will not connect to the VPN and you have a client call at 2?” (clarify).</li>
<li>Ask an open-ended question: “What happens on screen when you try to connect?”</li>
<li>Set expectations: “I will call you back by 12:30 with either a fix or a loan laptop.” Call back on time.</li>
<li>Document the work in plain language and follow up the next day.</li></ol>''')}
{scenario('the technician who was always on the phone', '''<p>Feedback says an on-site technician is skilled but users feel ignored: he takes personal calls during visits, uses
acronyms, and reads documents left on desks while he waits. The team lead coaches him: phone on silent, plain language, explain what
he is doing, and never read printouts or screens that are not part of the job. User satisfaction scores recover within a month.</p>''')}
{cfu(('Why use open-ended questions?', 'They get the user to describe the problem in their own words, which gives more detail.'),
     ('What should you do if you will be late to an appointment?', 'Contact the customer before the agreed time and give a new time.'),
     ('Name two behaviours to avoid with a difficult customer.', 'Arguing or being defensive, and minimising or judging their problem.'))}
'''

SUPPLEMENTS = [
    {'course': 'ITSUP', 'chapter': 12, 'lesson': 2, 'id': 'cert-incident-licensing', 'title': 'Incident handling, licensing and regulated data',
     'cert': ['A2:4.6'], 'html': sme_note('Prohibited content, incident handling, licensing, regulated data and policies (A+ Core 2 4.6).') + HTML_POL,
     'sources': ['nist-80086', 'rfc3227', 'osi-osd', 'pci-dss', 'hhs-hipaa']},
    {'course': 'ITSUP', 'chapter': 1, 'lesson': 4, 'id': 'cert-professionalism', 'title': 'Communication and professionalism',
     'cert': ['A2:4.7'], 'html': sme_note('Communication techniques and professionalism (A+ Core 2 4.7).') + HTML_PRO,
     'sources': ['comptia-a2-obj']},
]

GLOSSARY = [
    ('Chain of custody', 'Record of who held evidence, when and why, from collection onward.'),
    ('Order of volatility', 'Collecting the evidence that disappears fastest first (RFC 3227).'),
    ('Write blocker', 'Device that lets a drive be read for imaging without any writes to it.'),
    ('EULA', 'End-user licence agreement: the legal terms for using software.'),
    ('Perpetual licence', 'Pay once to use a version indefinitely.'),
    ('Subscription licence', 'Pay per period; the right to use ends when payment stops.'),
    ('PII', 'Personally identifiable information.'),
    ('AUP', 'Acceptable use policy: the rules for using company systems.'),
    ('Open-ended question', 'A question that cannot be answered yes or no, used to gather detail.'),
]

MISCONCEPTIONS = {
    'MC-C-IT12-INVESTIGATE-SELF': {'obj': 'IT-12.2', 'label': 'Investigating, copying or deleting prohibited content yourself instead of stopping and reporting',
                                   'fix': 'Stop, report to management, preserve; the finder is a witness, not the investigator.', 'terms': ['report', 'management', 'law enforcement', 'preserve']},
    'MC-C-IT12-CUSTODY-GAP': {'obj': 'IT-12.2', 'label': 'Thinking evidence stays usable without a chain-of-custody record or a forensic copy',
                              'fix': 'Log every hand-over and image through a write blocker with a hash.', 'terms': ['chain of custody', 'write blocker', 'hash', 'forensic']},
    'MC-C-IT12-VOLATILITY': {'obj': 'IT-12.2', 'label': 'Collecting disk or archives before memory and other volatile data',
                             'fix': 'Collect the most volatile data first: cache and memory before disk.', 'terms': ['order of volatility', 'memory', 'volatile']},
    'MC-C-IT12-LICENCE-SCOPE': {'obj': 'IT-12.2', 'label': 'Assuming a personal, free or open-source licence allows any use with no conditions',
                                'fix': 'Personal-use licences usually exclude business use; open-source licences carry conditions.', 'terms': ['eula', 'personal use', 'open source', 'licence']},
    'MC-C-IT12-DATA-REG': {'obj': 'IT-12.2', 'label': 'Matching regulated data to the wrong rules (e.g. card data to HIPAA)',
                           'fix': 'Card data falls under PCI DSS; U.S. health data under HIPAA; IDs and names are PII.', 'terms': ['pci', 'hipaa', 'pii', 'regulated']},
    'MC-C-IT1-ARGUE': {'obj': 'IT-1.4', 'label': 'Arguing, defending or minimising when a customer is upset',
                       'fix': 'Listen, do not argue or minimise, restate the problem and set expectations.', 'terms': ['listen', 'argue', 'difficult', 'restate']},
    'MC-C-IT1-JARGON': {'obj': 'IT-1.4', 'label': 'Explaining with jargon and acronyms to a non-technical user',
                        'fix': 'Use plain language and avoid acronyms.', 'terms': ['jargon', 'plain language', 'acronym']},
    'MC-C-IT1-CLOSED-Q': {'obj': 'IT-1.4', 'label': 'Using closed yes/no questions when you need the user to describe the problem',
                          'fix': 'Ask open-ended questions, then restate to confirm.', 'terms': ['open-ended', 'clarify', 'restate']},
    'MC-C-IT1-PRIVACY-LOOK': {'obj': 'IT-1.4', 'label': 'Reading or handling confidential material that is not part of the job',
                              'fix': 'Do not look at, copy or share confidential materials on desks, screens or printers.', 'terms': ['confidential', 'private', 'discretion']},
}

ITEMS = [
    order('A2:4.6', 'IT-12.2', 11, 'A technician finds what appears to be prohibited content on a laptop. Put the actions in order.',
          ['Stop work without browsing further or deleting anything', 'Inform management through the proper channel',
           'Secure the device and start a chain-of-custody record', 'Document what was seen and every action taken'],
          'Stop, report, preserve with custody, document (A+ Core 2 4.6).'),
    single('A2:4.6', 'IT-12.2', 12, 'Why is a forensic copy of a drive made through a write blocker and hashed?',
           'To prove the copy matches the original and nothing was changed',
           ['To compress the drive so it fits on a smaller disk', 'To remove the prohibited files from the copy', 'To make the drive bootable in another PC'],
           'Write blocking and hashing preserve and prove data integrity (NIST SP 800-86).',
           mc=[None, 'MC-C-IT12-INVESTIGATE-SELF', None]),
    single('A2:4.6', 'IT-12.2', 13, 'Following the order of volatility, which should be collected first from a running, compromised server?',
           'The contents of memory (RAM)', ['A full image of the hard drive', 'Last month’s backup tapes', 'The building’s network diagram'],
           'RFC 3227: collect the most volatile data first; memory is lost at power-off.',
           mc=['MC-C-IT12-VOLATILITY', 'MC-C-IT12-VOLATILITY', None]),
    match('A2:4.6', 'IT-12.2', 14, 'Match each kind of data to the rule set that most directly governs it.',
          [('Stored payment card numbers', 'PCI DSS'), ('Patient records at a U.S. clinic', 'HIPAA'),
           ('Rules for how staff may use company laptops', 'Acceptable use policy'), ('Secrets shared with a partner company', 'NDA')],
          'A+ Core 2 4.6 regulated data and policy.', decoys=['EULA']),
    single('A2:4.6', 'IT-12.2', 15, 'An application licence says “free for personal, non-commercial use”. Staff want it on 30 work PCs. What applies?',
           'A commercial (corporate) licence must be bought first', ['It may be installed because it is free',
            'It may be installed if it is open source', 'It may be installed if each user accepts the EULA'],
           'Personal-use licences do not cover business use; check the EULA and buy the right licence.',
           mc=['MC-C-IT12-LICENCE-SCOPE', 'MC-C-IT12-LICENCE-SCOPE', 'MC-C-IT12-LICENCE-SCOPE']),
    single('A2:4.7', 'IT-1.4', 11, 'A user says “It just doesn’t work!” Which response best clarifies the problem?',
           '“What happens on the screen when you try to sign in?”', ['“Is it plugged in?”', '“Have you tried turning it off and on?”',
            '“That usually works fine for everyone else.”'],
           'An open-ended question gets a description; the last option minimises the problem.',
           mc=['MC-C-IT1-CLOSED-Q', 'MC-C-IT1-CLOSED-Q', 'MC-C-IT1-ARGUE']),
    multi('A2:4.7', 'IT-1.4', 12, 'An angry customer blames IT for a lost file. Which TWO actions are professional? (Choose two.)',
          ['Listen without interrupting, then restate the problem', 'Set a clear time for the next update and meet it'],
          ['Explain that the customer probably deleted it', 'Describe the RAID controller’s write-cache policy in detail', 'Take a personal call while they calm down'],
          'Listen, clarify, set and meet expectations; do not blame, use jargon or get distracted.',
          mc=['MC-C-IT1-ARGUE', 'MC-C-IT1-JARGON', None]),
    single('A2:4.7', 'IT-1.4', 13, 'While waiting for an update to install, a technician sees a payroll printout on the user’s desk. What should they do?',
           'Leave it alone and not read it', ['Read it to understand the user’s workload', 'Photograph it to remind the user to secure it',
            'Move it into a drawer and read it later'],
           'Confidential materials are not part of the job: do not look, copy or handle them.',
           mc=['MC-C-IT1-PRIVACY-LOOK', 'MC-C-IT1-PRIVACY-LOOK', 'MC-C-IT1-PRIVACY-LOOK']),
    match('A2:4.7', 'IT-1.4', 14, 'Match each situation to the professional behaviour.',
          [('You will arrive 20 minutes late', 'Call the customer before the agreed time'), ('The user is not technical', 'Avoid jargon and acronyms'),
           ('The repair is finished', 'Document the work and follow up'), ('The laptop is not worth repairing', 'Offer repair or replacement options')],
          'A+ Core 2 4.7 communication and professionalism.', decoys=['Post about the visit on social media']),
]
