"""A+ Core 2 2.5 — social engineering attacks, threats and vulnerabilities (ITSUP 10.4)."""
from ..authoring import cfu, figure, match, multi, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-social', 'Verify-out-of-band decision for an unusual request',
    ['Unusual request\n(pay, reset, share)', 'Urgency, secrecy\nor new details?', 'Contact the sender\nby a known channel', 'Confirmed?\nThen proceed', 'Not confirmed?\nReport it'],
    'Five boxes in sequence. An unusual request arrives: to pay, to reset a password or MFA, or to share data. Ask whether it '
    'carries urgency, secrecy or changed details such as new bank details. If so, contact the requester through a channel '
    'you already trust — the number in the directory, not the one in the message. If they confirm, proceed under normal '
    'policy; if not, report the message to security and do not act on it.',
    'The control that beats most social engineering is a second, trusted channel — never the contact details in the message itself.', cols=5)

HTML = f'''
<p>Social engineering attacks the person, not the PC. Core 2 2.5 groups the exam vocabulary into three lists:
<strong>social engineering</strong> techniques, wider <strong>threats</strong>, and <strong>vulnerabilities</strong> that
make attacks succeed. A help-desk technician meets all three, often on the same ticket.</p>
<h4>Social engineering techniques</h4>
<ul>
<li><strong>Phishing</strong> — fraudulent email (or message) that gets the target to click, sign in or open an attachment.
<strong>Spear phishing</strong> targets a named person with researched details; <strong>whaling</strong> targets executives.
<strong>Vishing</strong> is voice phishing (a phone call), <strong>smishing</strong> uses SMS, and <strong>QR code phishing</strong>
hides the malicious link in a QR code so email filters cannot read it.</li>
<li><strong>Impersonation / pretexting</strong> — the attacker plays a role (new hire, auditor, “IT support”) with a believable story.</li>
<li><strong>Shoulder surfing</strong> — watching someone type a PIN or password. <strong>Tailgating</strong> — following an
authorised person through a secure door. <strong>Dumpster diving</strong> — recovering useful paper or media from the rubbish.</li>
</ul>
<h4>Threats</h4>
<p><strong>DoS / DDoS</strong> (exhausting a service, from one or many sources); <strong>evil twin</strong> (a rogue access point
using a trusted network name); <strong>zero-day</strong> (a flaw with no patch yet); <strong>spoofing</strong> (forged
sender, caller ID, address or site); <strong>on-path</strong> attacks (intercepting traffic between two parties);
<strong>brute-force</strong> and <strong>dictionary</strong> password attacks; the <strong>insider threat</strong>;
<strong>SQL injection</strong> and <strong>cross-site scripting (XSS)</strong> against web applications;
<strong>business email compromise (BEC)</strong> — using a real or look-alike business mailbox to redirect payments; and
<strong>supply chain</strong> attacks through a trusted vendor or update.</p>
<h4>Vulnerabilities</h4>
<p><strong>Non-compliant</strong> systems (failing the organisation’s baseline), <strong>unpatched</strong> systems,
<strong>unprotected</strong> systems (missing antivirus or firewall), <strong>end-of-life (EOL)</strong> operating systems
that no longer receive security updates, and <strong>bring-your-own-device (BYOD)</strong> devices the organisation does not fully control.</p>
{_FIG}
<p>CISA’s guidance is consistent across all of these: be suspicious of unsolicited contact, do not use contact details
supplied in the message, verify through a known channel, and report attempts. NIST SP 800-63B-4 adds the technical
control: <strong>phishing-resistant authenticators</strong> (such as security keys or passkeys) cannot be replayed to a fake
sign-in page, which defeats the most common phishing goal.</p>
{worked('the changed bank details', '''<ol>
<li>Accounts payable receives an email from a regular supplier: “our bank has changed, please pay this invoice to the new account today”.</li>
<li>Red flags: urgency, changed payment details, and a reply-to address one letter different from the real domain — a BEC attempt.</li>
<li>Do not reply to the email or call the number in it. Call the supplier on the number already held in the finance system.</li>
<li>The supplier confirms nothing changed. Report the message to security, who block the look-alike domain and search for other copies.</li>
<li>Document the ticket; the lesson for the team is the out-of-band check, which costs one phone call.</li></ol>''')}
{scenario('the “IT support” caller', '''<p>A user rings the help desk to say “IT” just called and asked her to read out the code her authenticator app
showed. She did. That is vishing aimed at MFA: the attacker already had her password. Treat it as a compromised account —
reset the password, revoke sessions and re-register MFA according to policy, check sign-in logs, and escalate to
security. Remind her that the help desk never asks for MFA codes.</p>''')}
{cfu(('What is the difference between spear phishing and whaling?', 'Spear phishing targets a specific person with researched details; whaling is spear phishing aimed at senior executives.'),
     ('Why are QR codes used in phishing?', 'The link is in an image, so email filters and users cannot easily read where it goes.'),
     ('Name the one habit that defeats most BEC and vishing attempts.', 'Verifying the request through a separate, already-known channel.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 10, 'lesson': 4, 'id': 'cert-social',
    'title': 'Social engineering attacks, threats and vulnerabilities',
    'cert': ['A2:2.5'],
    'html': sme_note('Social engineering, threats and vulnerabilities vocabulary (Core 2 2.5).') + HTML,
    'sources': ['cisa-phish', 'nist-80063b4'],
}]

GLOSSARY = [
    ('Vishing', 'Voice phishing: a phone call that tricks the target into revealing information or taking an action.'),
    ('Smishing', 'Phishing by SMS text message.'),
    ('Whaling', 'Spear phishing aimed at senior executives.'),
    ('Business email compromise (BEC)', 'Fraud that uses a real or look-alike business mailbox to redirect payments or obtain data.'),
    ('Evil twin', 'A rogue wireless access point that advertises a trusted network name to intercept users’ traffic.'),
    ('Zero-day', 'A vulnerability that is being exploited before the vendor has released a fix.'),
]

ITEMS = [
    match('A2:2.5', 'IT-10.4', 1, 'Match each attack to its description.',
          [('A text message with a fake parcel-delivery link', 'Smishing'),
           ('A phone call from someone posing as the bank', 'Vishing'),
           ('An email to the CFO naming a real acquisition', 'Whaling'),
           ('A poster with a QR code to a fake sign-in page', 'QR code phishing')],
          'Smishing is SMS, vishing is voice, whaling targets executives, and QR code phishing hides the link in an image.',
          decoys=['Dumpster diving']),
    single('A2:2.5', 'IT-10.4', 2, 'An employee holds the secure door open for a stranger carrying boxes who has no badge. Which attack has succeeded?',
           'Tailgating',
           ['Shoulder surfing', 'Dumpster diving', 'Impersonation by email'],
           'Following an authorised person through a secure entrance is tailgating.'),
    single('A2:2.5', 'IT-10.4', 3, 'A supplier’s email asks accounts payable to send today’s payment to a new bank account. What should the clerk do?',
           'Call the supplier on the number already on file',
           ['Reply to the email to ask if it is genuine', 'Pay it, because the invoice number is correct', 'Call the phone number given in the email'],
           'BEC relies on the victim using the attacker’s contact details; verify out of band using a known channel.'),
    multi('A2:2.5', 'IT-10.4', 4, 'Which TWO are vulnerabilities rather than attacks? (Choose two.)',
          ['A laptop still running an end-of-life OS', 'A PC with its firewall and antivirus disabled'],
          ['An evil twin access point', 'A dictionary attack on a login page', 'A vishing call to the help desk'],
          'EOL and unprotected systems are weaknesses that attacks exploit; the others are attacks or threats.'),
    single('A2:2.5', 'IT-10.4', 5, 'Hundreds of compromised home routers flood a company’s web server with requests until it stops responding. What is this?',
           'A distributed denial-of-service attack',
           ['An on-path attack intercepting the server’s traffic', 'A zero-day exploit', 'A supply chain attack'],
           'Many sources exhausting one service is DDoS.'),
]
