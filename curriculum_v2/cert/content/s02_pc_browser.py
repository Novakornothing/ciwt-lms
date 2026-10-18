"""A+ Core 2 3.4 (PC security symptoms) and 2.11 (browser security settings) — ITSUP 10.2."""
from ..authoring import cfu, figure, match, multi, order, scenario, single, sme_note, worked

_FIG = figure(
    'fig-c-browser', 'Where a browser redirect can come from',
    ['Malicious\nextension', 'Browser proxy\nsetting', 'hosts file /\nDNS setting', 'Router or\nupstream DNS', 'Website itself\n(compromised)'],
    'Five possible sources of a redirect, from closest to the user outward: a malicious browser extension, a proxy '
    'setting in the browser or operating system, an entry in the hosts file or a changed DNS server on the PC, a '
    'changed DNS setting on the router or upstream, and finally a compromised website. Test from the inside out: '
    'a different browser profile with no extensions, then the proxy and hosts file, then another device on the '
    'same network. If another device is redirected too, the cause is upstream of the PC.',
    'Work from the inside out; a second device on the same network tells you which side of the PC the fault is on.', cols=5)

HTML = f'''
<p>Core 2 objective 3.4 is a list of <em>symptoms</em> that should make a technician suspect a security problem on a
PC, and objective 2.11 is the browser configuration that prevents most of them. Learn them together: the browser is
where most of these symptoms first appear.</p>
<h4>Symptoms that point at compromise</h4>
<ul>
<li><strong>Operating system:</strong> desktop alerts and <strong>false antivirus alerts</strong> from software the
organisation did not install (“scareware” that wants payment or a download); <strong>unwanted OS notifications</strong>;
<strong>OS update failures</strong> (some malware blocks updates and security tools); files that are
<strong>missing, renamed or cannot be opened</strong> (a new extension on many files is a ransomware warning — isolate the
PC immediately); and being <strong>unable to access the network</strong> after malware changes proxy or DNS settings.</li>
<li><strong>Browser:</strong> random <strong>pop-ups</strong>, <strong>certificate warnings</strong> on well-known sites,
<strong>redirection</strong> to search pages or sites the user did not ask for, and <strong>degraded browser
performance</strong>.</li>
</ul>
<p>Not every symptom means malware. A certificate warning on <em>every</em> site usually means the PC clock is wrong,
because certificates are only valid between two dates; fix the time and retest before suspecting interception. A flood
of “notifications” on the desktop is very often a website the user allowed to send notifications, which you revoke in the
browser’s site settings. When the evidence does point at malware, follow the malware-removal procedure (Core 2 2.6):
investigate and verify the symptoms, quarantine (disconnect) the system, disable System Restore (Windows Home), remediate
(update the anti-malware tools, scan and remove), schedule scans and run updates, enable System Restore and create a
restore point, then educate the user.</p>
{_FIG}
<h4>Browser security settings (Core 2 2.11)</h4>
<table class="ref-table"><thead><tr><th scope="col">Setting</th><th scope="col">What to do</th></tr></thead><tbody>
<tr><td>Installation source</td><td>Install browsers and extensions only from the vendor or the official store; where the vendor publishes a hash, verify it (PowerShell <code>Get-FileHash</code>) — untrusted download sites bundle adware.</td></tr>
<tr><td>Patching</td><td>Keep automatic browser updates on; browsers are patched often because they parse untrusted content.</td></tr>
<tr><td>Extensions and plug-ins</td><td>Install few, from the official store; remove ones the user does not recognise; disable rather than delete while troubleshooting.</td></tr>
<tr><td>Password manager</td><td>Use the browser’s or the organisation’s password manager, with a strong primary password and MFA on the account.</td></tr>
<tr><td>Certificates</td><td>Check for HTTPS and a valid certificate before signing in; never click through a warning on a site that handles credentials.</td></tr>
<tr><td>Pop-up and ad blocking</td><td>Keep the pop-up blocker on; allow pop-ups per site only when a business app needs them. Ad blockers cut malvertising but may break some sites.</td></tr>
<tr><td>Clearing data</td><td>Clearing browsing data, cache and cookies fixes stale pages and signs the user out of sites.</td></tr>
<tr><td>Private browsing</td><td>Incognito / InPrivate stops the browser keeping local history and cookies after the window closes; it does <em>not</em> hide activity from websites, the employer or the internet provider.</td></tr>
<tr><td>Sign-in and data sync</td><td>Browser sync copies passwords and history to every signed-in device; on shared or corporate PCs follow policy before turning it on.</td></tr>
<tr><td>Proxy and secure DNS</td><td>A proxy setting nobody configured is a redirect suspect. Secure DNS (DNS over HTTPS) encrypts lookups; corporate policy may manage it.</td></tr>
</tbody></table>
{worked('redirected searches', '''<ol>
<li>User reports searches “go to a different search site”. Another PC on the same Wi-Fi is fine, so the cause is on this PC.</li>
<li>A new browser profile with no extensions searches normally, so the cause is in the user’s profile.</li>
<li>Extensions list shows “PDF Converter Pro”, installed yesterday from a pop-up. Disable it; searches are normal again.</li>
<li>Remove the extension, reset the browser’s search engine and start-up page, run a full scan, and check the proxy
setting and hosts file for anything else it changed.</li>
<li>Document the extension name and educate the user: extensions only from the official store, and only when needed.</li></ol>''')}
{scenario('the renamed files', '''<p>A finance user says her spreadsheets “will not open” and every file in a shared folder now ends in
<code>.lockd</code>. This is a ransomware pattern, not a broken Office install. You unplug the PC’s network cable
(or disable Wi-Fi), leave it powered on for the incident team, tell your supervisor, and record what you saw and when.
You do not try to rename the files back or run random decryption tools; recovery is from backups once the incident
team says so.</p>''')}
{cfu(('Every HTTPS site shows a certificate warning on one PC. What do you check first, and why?', 'The date and time — certificates are valid only between two dates, so a wrong clock fails them all.'),
     ('What does private browsing protect against, and what does it not?', 'It stops local history and cookies being kept; it does not hide activity from websites, the employer or the ISP.'),
     ('Searches are redirected on one PC but not on another on the same network. Where is the cause?', 'On the first PC — an extension, a proxy setting, the hosts file or its DNS setting.'))}
'''

SUPPLEMENTS = [{
    'course': 'ITSUP', 'chapter': 10, 'lesson': 2, 'id': 'cert-pc-browser',
    'title': 'PC security symptoms and browser security settings',
    'cert': ['A2:3.4', 'A2:2.11'],
    'html': sme_note('PC security symptoms (Core 2 3.4) and browser security settings (Core 2 2.11).') + HTML,
    'sources': ['ms-smartscreen', 'chrome-help', 'cisa-phish'],
}]

GLOSSARY = [
    ('Scareware', 'Fake security warning that frightens the user into paying or installing software.'),
    ('Browser redirection', 'The browser sends the user to pages they did not request, usually because of an extension, proxy, hosts-file or DNS change.'),
    ('Private browsing', 'Incognito / InPrivate mode: no local history or cookies are kept after the window closes; activity is still visible to sites and networks.'),
    ('Secure DNS', 'Browser setting that sends DNS lookups over an encrypted connection (DNS over HTTPS).'),
    ('File hash', 'A fixed-length value computed from a file (for example SHA-256); matching the vendor’s published hash shows the download was not altered.'),
]

ITEMS = [
    single('A2:3.4', 'IT-10.2', 1, 'A PC shows a full-screen “Your computer is infected — call this number” warning from software nobody installed. What is this most likely to be?',
           'Scareware posing as a security product',
           ['A genuine Microsoft Defender alert', 'A failed Windows Update notification', 'A certificate warning from the browser'],
           'Fake antivirus alerts that demand a call or payment are a Core 2 3.4 symptom; genuine Defender alerts do not ask for a phone call.'),
    single('A2:3.4', 'IT-10.2', 2, 'One laptop shows certificate warnings on every HTTPS site, including the bank and Microsoft. Other laptops are fine. What should the technician check first?',
           'The laptop’s date, time and time zone',
           ['The certificates on each website', 'The laptop’s screen resolution', 'The Wi-Fi channel the laptop uses'],
           'Certificates are only valid between two dates; a wrong clock fails every site at once. Fix it before suspecting interception.'),
    multi('A2:3.4', 'IT-10.2', 3, 'Which THREE symptoms should make a technician suspect malware on a Windows PC?',
          ['Many files suddenly have a new, unknown extension', 'Windows Update and the antivirus fail to update', 'Searches are redirected to an unfamiliar site'],
          ['The taskbar is set to auto-hide', 'Night light turns on at sunset', 'Display scaling is set to 125 percent'],
          'Renamed files, blocked updates and redirection are all 3.4 symptoms; the others are ordinary settings.'),
    order('A2:3.4', 'IT-10.2', 4, 'Put the malware-removal steps in the order the A+ procedure uses.',
          ['Investigate and verify the symptoms', 'Quarantine the infected system', 'Disable System Restore (Windows Home)',
           'Remediate: update tools, scan and remove', 'Enable System Restore and create a restore point', 'Educate the end user'],
          'The published Core 2 2.6 order: investigate and verify, quarantine, disable System Restore, remediate (update tools, scan and remove, schedule scans and updates), enable System Restore and create a restore point, educate.'),
    single('A2:2.11', 'IT-10.2', 1, 'A user wants to download a free PDF tool. The vendor publishes a SHA-256 value for the installer. What is that value for?',
           'Confirming the downloaded file was not altered',
           ['Unlocking the paid version of the tool', 'Encrypting the file during the download', 'Registering the tool with Windows Update'],
           'A hash lets you verify integrity: compute it (Get-FileHash) and compare with the vendor’s published value.'),
    single('A2:2.11', 'IT-10.2', 2, 'A user believes Incognito mode stops their employer seeing which websites they visit. What should you tell them?',
           'It only stops the browser keeping local history',
           ['It encrypts all traffic so nobody can see it', 'It routes traffic through a private VPN server', 'It blocks the employer’s proxy from logging it'],
           'Chrome Help is explicit: Incognito does not hide activity from websites, an employer or school, or the internet provider.'),
    match('A2:2.11', 'IT-10.2', 3, 'Match each browser problem to the setting that best addresses it.',
          [('A banking site keeps showing an old page after an update', 'Clear cache and cookies'),
           ('Adverts on news sites have delivered malware', 'Ad blocker'),
           ('An unknown toolbar appeared after a free download', 'Extensions / add-ons'),
           ('A user reuses one weak password everywhere', 'Password manager')],
          'Each fix targets the cause: stale data, malvertising, an unwanted extension, password reuse. Private browsing fixes none of them.',
          decoys=['Private browsing']),
    multi('A2:2.11', 'IT-10.2', 4, 'Which TWO actions harden a corporate browser installation? (Choose two.)',
          ['Keep automatic browser updates turned on', 'Allow extensions only from the official store'],
          ['Turn off the pop-up blocker for all sites', 'Click through certificate warnings on intranet sites', 'Install the browser from a mirror site'],
          'Patching and trusted extension sources reduce risk; the others weaken security.'),
]
