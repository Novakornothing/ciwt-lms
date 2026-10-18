"""A+ Core 2 4.9 — remote access technologies (ITSUP 9.3)."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-remote', 'Safe remote support session',
    ['Verify the user\nand the ticket', 'Get consent for\nscreen access', 'Connect via approved\ntool (VPN / gateway)', 'Do the work;\nuser can watch', 'End session;\nlog it'],
    'Five boxes in order. Verify who the user is and that there is a ticket; get the user’s consent before viewing or '
    'controlling their screen; connect only with an approved tool, through the VPN or remote-desktop gateway rather than a '
    'port opened to the internet; do the work while the user can watch; then end the session, confirm it is closed, and '
    'record it on the ticket.',
    'Remote access is a powerful door into the network: approved tools, authenticated users, consent and a log.', cols=5)

HTML = f'''
<table class="ref-table"><thead><tr><th scope="col">Method</th><th scope="col">What it is</th><th scope="col">Security considerations</th></tr></thead><tbody>
<tr><td><strong>RDP</strong></td><td>Windows Remote Desktop (TCP 3389): full desktop session</td><td>Never expose 3389 directly to the internet; use a VPN or Remote Desktop Gateway, Network Level Authentication and MFA.</td></tr>
<tr><td><strong>VPN</strong></td><td>Encrypted tunnel into the network, used <em>with</em> other tools</td><td>MFA; keep the VPN appliance patched — it faces the internet.</td></tr>
<tr><td><strong>VNC</strong></td><td>Cross-platform screen sharing using the RFB protocol (RFC 6143)</td><td>Authentication is often weak and traffic may be unencrypted — tunnel it over SSH or a VPN.</td></tr>
<tr><td><strong>SSH</strong></td><td>Encrypted command-line access (TCP 22), mainly Linux, macOS and network devices</td><td>Key-based authentication, disable password login and direct root login where possible.</td></tr>
<tr><td><strong>RMM</strong></td><td>Remote monitoring and management platform used by IT teams and MSPs</td><td>A compromise reaches every managed device; CISA has warned of attackers abusing legitimate RMM tools. MFA, least privilege, approved tools only.</td></tr>
<tr><td><strong>SPICE</strong></td><td>Remote display protocol for virtual machines (commonly with KVM/QEMU)</td><td>Restrict to the management network; enable TLS.</td></tr>
<tr><td><strong>WinRM</strong></td><td>Windows Remote Management for PowerShell remoting (HTTP 5985, HTTPS 5986)</td><td>Use HTTPS or a domain-authenticated session; restrict who can connect.</td></tr>
<tr><td><strong>Third-party tools</strong></td><td>Screen-sharing and videoconferencing apps, file-transfer software, desktop-management software</td><td>Only the organisation’s approved tools — attackers use the same apps in tech-support scams.</td></tr>
</tbody></table>
{_FIG}
{worked('choosing the tool', '''<ol>
<li>A user at home cannot open a line-of-business app; you need to see her screen. She is on the company VPN.</li>
<li>Use the approved screen-sharing tool, which asks her to accept the session — consent is built in.</li>
<li>Later that day you must restart a service on 30 servers: PowerShell remoting over WinRM from the admin workstation, not 30 RDP sessions.</li>
<li>A Linux web server needs a config check: SSH with your key, through the jump host.</li></ol>''')}
{scenario('the unexpected caller', '''<p>A user says “Microsoft support” phoned and asked her to install a screen-sharing app so they could fix a virus.
Microsoft does not make unsolicited support calls. Treat it as a tech-support scam: disconnect the PC from the network if the
app was installed and a session took place, remove the app, scan, reset any passwords typed during the session from a clean
device, and report it to security.</p>''')}
{cfu(('Why should RDP not be published directly to the internet?', 'It is heavily targeted; put it behind a VPN or Remote Desktop Gateway with NLA and MFA.'),
     ('Which remote method suits running the same PowerShell command on many Windows servers?', 'WinRM (PowerShell remoting).'),
     ('Why is VNC usually tunnelled over SSH or a VPN?', 'Its authentication and encryption are often weak.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 9, 'lesson': 3, 'id': 'cert-remote', 'title': 'Remote access technologies and their security',
    'cert': ['A2:4.9'], 'html': sme_note('Remote access methods and security considerations (Core 2 4.9).') + HTML,
    'sources': ['ms-rdp', 'rfc6143', 'cisa-rmm'],
}]

GLOSSARY = [
    ('RMM', 'Remote monitoring and management: a platform for managing many endpoints remotely.'),
    ('WinRM', 'Windows Remote Management: the service behind PowerShell remoting (ports 5985/5986).'),
    ('VNC', 'Virtual Network Computing: cross-platform screen sharing using the RFB protocol.'),
    ('SPICE', 'Simple Protocol for Independent Computing Environments: a remote display protocol for virtual machines.'),
]

ITEMS = [
    match('A2:4.9', 'IT-9.3', 1, 'Match each remote access method to its best use.',
          [('RDP', 'Full desktop session on a Windows PC'), ('SSH', 'Encrypted command line on a Linux server'),
           ('WinRM', 'PowerShell commands on many Windows servers'), ('RMM', 'Monitoring and patching hundreds of managed endpoints')],
          'Each method has a typical job in Core 2 4.9.',
          decoys=['SPICE for printers']),
    single('A2:4.9', 'IT-9.3', 2, 'A small firm wants staff to use Remote Desktop to office PCs from home. What is the most secure approach?',
           'Require the VPN (or an RD Gateway) with MFA',
           ['Forward TCP 3389 to each PC', 'Use VNC without a password', 'Allow RDP from the internet only during business hours'],
           'Do not expose RDP directly; tunnel it through an authenticated gateway.'),
    single('A2:4.9', 'IT-9.3', 3, 'Which protocol is a remote display protocol designed for virtual machines?',
           'SPICE',
           ['SMTP', 'LDAP', 'SNMP'],
           'SPICE provides remote display for VMs (commonly KVM/QEMU).'),
    multi('A2:4.9', 'IT-9.3', 4, 'Which TWO practices should apply to every remote support session on a user’s screen? (Choose two.)',
          ['Get the user’s consent first', 'Use only the organisation’s approved tool'],
          ['Ask the user for their password', 'Disable the user’s antivirus', 'Leave the session open for follow-up'],
          'Consent and approved tools; never ask for passwords or weaken protection.'),
]
