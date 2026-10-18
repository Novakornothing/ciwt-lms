"""A+ Core 2 4.10 — basic AI concepts (ITSUP 12.2)."""
from ..authoring import cfu, figure, match, multi, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-ai', 'Checks before using an AI tool on a work task',
    ['Is this tool\napproved by policy?', 'Is the data allowed\nin this tool?', 'Use it; treat output\nas a draft', 'Verify facts,\nsources and bias', 'Record and disclose\nAI use if required'],
    'Five boxes in order. First, is this AI tool approved under the organisation’s appropriate-use policy? Second, is the '
    'data you would enter allowed in it — public tools may keep or learn from prompts, depending on the provider’s terms. '
    'Third, use it, and treat what it produces as a draft. Fourth, verify facts, sources and possible bias before anyone '
    'relies on the output. Fifth, record or disclose the AI use where policy requires it.',
    'Policy and data checks come before the prompt; verification comes before anyone relies on the answer.', cols=5)

HTML = f'''
<p>AI assistants now appear inside operating systems, office suites, browsers and ticketing tools (<strong>application
integration</strong>). Core 2 4.10 asks technicians to understand the policy, the limitations and the difference between
public and private tools — because users will ask the help desk about all three.</p>
<h4>Policy</h4>
<p>An <strong>appropriate-use policy</strong> for AI says which tools are approved, what data may be entered, and when AI use
must be disclosed. <strong>Plagiarism</strong> is part of it: presenting AI-generated text or code as your own original work,
or reproducing copyrighted material it outputs, can breach academic, employment or licensing rules.</p>
<h4>Limitations</h4>
<ul>
<li><strong>Hallucinations</strong> — the model produces fluent, confident content that is false (NIST AI 600-1 calls this
“confabulation”), including commands, citations or settings that do not exist.</li>
<li><strong>Accuracy</strong> — output can be out of date or wrong for your version; verify against vendor documentation.</li>
<li><strong>Bias</strong> — models reflect patterns in their training data and can produce unfair or skewed results.</li>
</ul>
<h4>Private vs. public</h4>
<p>A <strong>public</strong> AI service is open to anyone; depending on the provider’s terms, prompts may be retained or used to
improve the service. A <strong>private</strong> or enterprise deployment is contracted or hosted for the organisation, with
controls on where data is stored and who can see it. Three questions decide which to use: <strong>data security</strong>
(who can access what you enter), <strong>data source</strong> (what the model was trained on, or which internal documents it
can search), and <strong>data privacy</strong> (personal data must not go into a tool the organisation has not approved for it).</p>
{_FIG}
{worked('checking an AI-suggested fix', '''<ol>
<li>An AI assistant suggests a PowerShell command to “reset the Windows Update cache”.</li>
<li>Before running it, look the cmdlet up in Microsoft Learn: one parameter it used does not exist — a hallucination.</li>
<li>Use the documented procedure instead, and note on the ticket that the AI suggestion was checked and not used.</li></ol>''')}
{scenario('the customer list', '''<p>A sales user asks why the public chatbot she uses at home is blocked at work; she wants to paste a customer
spreadsheet in and ask for a summary. You explain that the spreadsheet holds personal data, and that the public tool is not
approved for it under the AI use policy. You point her to the organisation’s approved enterprise assistant, which is
configured to keep data within the company’s tenant, and remind her to check the summary before sending it on.</p>''')}
{cfu(('What is an AI hallucination?', 'Confident, fluent output that is false — for example a command or citation that does not exist.'),
     ('Why might a public AI tool be unsuitable for customer data?', 'Depending on the provider’s terms, prompts may be retained or used for training, and the tool is not approved for personal data.'),
     ('Name the three Core 2 4.10 limitations.', 'Bias, hallucinations and accuracy.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 12, 'lesson': 2, 'id': 'cert-ai',
    'title': 'AI tools at work: policy, limitations, and private vs. public',
    'cert': ['A2:4.10'],
    'html': sme_note('Basic AI concepts for support staff (Core 2 4.10).') + HTML,
    'sources': ['nist-ai6001', 'nist-ai1001'],
}]

GLOSSARY = [
    ('Hallucination (AI)', 'Fluent but false output from a generative AI model; NIST AI 600-1 uses the term confabulation.'),
    ('AI appropriate-use policy', 'Rules on which AI tools may be used, with what data, and when AI use must be disclosed.'),
    ('Private (enterprise) AI', 'An AI service deployed or contracted for one organisation, with controls on data storage and access.'),
]

ITEMS = [
    single('A2:4.10', 'IT-12.2', 1, 'An AI assistant gives a technician a registry path that does not exist in any Windows version. What is this limitation called?',
           'A hallucination',
           ['A bias in the training data', 'A plagiarism violation', 'Application integration'],
           'Confident but false output is a hallucination (NIST: confabulation).'),
    single('A2:4.10', 'IT-12.2', 2, 'A user wants to paste a spreadsheet of customer names and addresses into a public AI chatbot. What is the main concern?',
           'Data privacy: personal data entering an unapproved tool',
           ['The chatbot will reformat the spreadsheet', 'The output will be too long to read', 'The browser will block the paste action'],
           'Public tools may retain prompts under the provider’s terms; personal data needs an approved tool.'),
    match('A2:4.10', 'IT-12.2', 3, 'Match each AI concern to the scenario that shows it.',
          [('Bias', 'A screening tool scores one group of applicants lower for no job reason'),
           ('Plagiarism', 'A student submits AI-written work as their own'),
           ('Accuracy', 'An answer describes settings from a version two releases old'),
           ('Data security', 'Prompts with internal designs are visible outside the company')],
          'Each scenario illustrates one Core 2 4.10 concept.',
          decoys=['A chatbot is built into the ticketing tool']),
    multi('A2:4.10', 'IT-12.2', 4, 'Which TWO are good practice before relying on an AI-generated troubleshooting step? (Choose two.)',
          ['Check the command against vendor documentation', 'Confirm the tool is approved by policy'],
          ['Run it on all PCs to see if it works', 'Accept it if the answer sounds confident', 'Paste in the user’s password for context'],
          'Verify against primary sources and use only approved tools; confidence is not accuracy.'),
]
