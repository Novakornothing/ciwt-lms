"""IT Support Fundamentals chapters 7–13 — core teaching content (pass 9, pending SME review).

The pass-8 audit found ITSUP chapters 7–13 thin (about 900–1,400 words each against 3,600–6,600 for
chapters 1–2). Each chapter module (ch07 … ch13) adds, per lesson:

* measurable lesson objectives (replacing the old "terminal objectives" list on the page),
* a core-content section with clear explanations, at least one worked example, a real-world
  troubleshooting scenario, a described diagram (SVG with title, description and long-text alternative)
  and check-for-understanding questions with hidden answers,

and, per chapter: chapter objectives (curriculum_v2.objectives), glossary terms, a lesson-plan update
and assessment items (≥ 2 per objective) with rationales.

The original lesson text in lessons.py is unchanged; this layer is applied by curriculum_v2.apply.
Everything here is tagged ``PENDING`` until a subject-matter expert signs it off. Facts were checked
against the sources in SOURCES (vendor documentation, NIST, CISA, IETF); see CURRICULUM_AUDIT.md.
"""
import hashlib
import math
from html import escape

from ..netops_core import table  # noqa: F401  (re-exported for chapter modules)

PENDING = 'Pending SME review'
PASS = 'pass 9'

SOURCES = {
    'ms-sfc': 'Microsoft Support — “Use the System File Checker tool to repair missing or corrupted system files” (run DISM /RestoreHealth before sfc /scannow)',
    'ms-recovery': 'Microsoft Support — “Recovery options in Windows” and “Fix issues by reinstalling the current version of Windows”',
    'ms-qmr': 'Microsoft Learn — Quick machine recovery (Windows 11)',
    'ms-lifecycle': 'Microsoft Learn — Windows lifecycle FAQ and Windows 11 release information (24 / 36-month servicing)',
    'ms-wmic': 'Microsoft Support — “WMIC removal from Windows” (removed from Windows 11 24H2/25H2, August 2026); Microsoft Learn — removed features',
    'ms-gp': 'Microsoft Learn — Group Policy processing; gpupdate command reference (90-minute refresh, 0–30 minute offset)',
    'ms-kerberos': 'Microsoft Learn — “Maximum tolerance for computer clock synchronization” (default 5 minutes)',
    'ms-bitlocker': 'Microsoft Support — “Device encryption in Windows” and “Find your BitLocker recovery key”',
    'ms-defender': 'Microsoft Learn — Microsoft Defender Offline scan in Windows',
    'ms-cmd': 'Microsoft Learn — Windows commands reference (ipconfig, netsh, tasklist, taskkill) and PowerShell module documentation (NetTCPIP, DnsClient, CimCmdlets)',
    'apple-recovery': 'Apple Support — “How to start up from macOS Recovery” and Mac User Guide (FileVault, Time Machine, Disk Utility First Aid, Activity Monitor)',
    'linux-man': 'Linux man-pages project and systemd documentation (chmod, chown, ip, ss, systemctl, journalctl)',
    'nist-80063b4': 'NIST SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management (2025)',
    'nist-80061r3': 'NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management (April 2025)',
    'nist-80088r2': 'NIST SP 800-88 Rev. 2, Guidelines for Media Sanitization (September 2025)',
    'rfc3227': 'IETF RFC 3227, Guidelines for Evidence Collection and Archiving (order of volatility)',
    'cisa-backup': 'CISA — “Back Up Business Data” (3-2-1 rule, test restores)',
    'cisa-mfa': 'CISA — Implementing phishing-resistant MFA (fact sheet)',
}


def sme_note(detail='Core content, objectives and checks added in pass 9.'):
    """Instructor-only tag; app.render_lesson strips instructor-note blocks for students."""
    return (f'<div class="instructor-note"><h4>{PENDING}</h4><p>{detail} Verify against local practice before '
            f'grading on it; facts were checked against the sources listed at the end of the section.</p></div>')


def sources_line(keys):
    return '<p class="ref-sources small">Sources: ' + '; '.join(escape(SOURCES[k]) for k in keys) + '.</p>'


def _lines(label):
    return label.split('\n')


def figure(fid, title, nodes, desc, caption, cols=4, loop=None):
    """A described flow diagram. ``nodes`` are short labels ('\\n' splits lines). ``desc`` is the long-text
    alternative shown under the figure; the SVG carries <title>/<desc> and role="img"."""
    W, H, GX, GY, PAD = 168, 70, 38, 48, 12
    n = len(nodes)
    cols = min(cols, n)
    rows = math.ceil(n / cols)
    width = cols * W + (cols - 1) * GX + 2 * PAD
    height = rows * H + (rows - 1) * GY + 2 * PAD + (34 if loop else 0)
    pos = [(PAD + (i % cols) * (W + GX), PAD + (i // cols) * (H + GY)) for i in range(n)]
    parts = [f'<svg class="flow-svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{fid}-t {fid}-d" '
             f'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">',
             f'<title id="{fid}-t">{escape(title)}</title><desc id="{fid}-d">{escape(desc)}</desc>',
             f'<defs><marker id="{fid}-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    for i, (x, y) in enumerate(pos):
        parts.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="10" class="flow-node{" flow-first" if i == 0 else ""}"/>')
        ls = _lines(nodes[i])
        y0 = y + H / 2 - (len(ls) - 1) * 8 + 5
        for j, line in enumerate(ls):
            parts.append(f'<text x="{x + W / 2}" y="{y0 + j * 16}" text-anchor="middle" class="flow-text">{escape(line)}</text>')
    for i in range(n - 1):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        if y1 == y2:
            parts.append(f'<line x1="{x1 + W}" y1="{y1 + H / 2}" x2="{x2 - 2}" y2="{y2 + H / 2}" class="flow-edge" marker-end="url(#{fid}-a)"/>')
        else:
            mid = y1 + H + GY / 2
            parts.append(f'<path d="M{x1 + W / 2},{y1 + H} V{mid} H{x2 + W / 2} V{y2 - 2}" class="flow-edge" fill="none" marker-end="url(#{fid}-a)"/>')
    if loop:
        a, b, label = loop
        (xa, ya), (xb, yb) = pos[a], pos[b]
        yl = height - PAD - 6
        parts.append(f'<path d="M{xa + W / 2},{ya + H} V{yl} H{xb + W / 2} V{yb + H + 2}" class="flow-edge flow-loop" fill="none" marker-end="url(#{fid}-a)"/>')
        parts.append(f'<text x="{(xa + xb + W) / 2}" y="{yl - 6}" text-anchor="middle" class="flow-text flow-small">{escape(label)}</text>')
    parts.append('</svg>')
    return (f'<figure class="lesson-figure" id="{fid}">{"".join(parts)}'
            f'<figcaption><strong>Figure.</strong> {caption}</figcaption>'
            f'<details class="figure-desc"><summary>Text description of the diagram</summary><p>{escape(desc)}</p></details></figure>')


def worked(title, body):
    return f'<div class="worked worked-example"><h4>Worked example — {title}</h4>{body}</div>'


def scenario(title, body):
    return f'<div class="scenario-box"><h4>Real-world scenario — {title}</h4>{body}</div>'


def cfu(*qa):
    items = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in qa)
    return f'<div class="check-box cfu"><h4>Check for understanding</h4>{items}</div>'


def section(title, body, sid=None):
    return f'<h3{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}>{title}</h3>{body}'


# ----------------------------------------------------------------------------------------- items
def item(obj, n, q, correct, wrong, why):
    assert len(wrong) == 3 and correct not in wrong and len(set(wrong)) == 3, (obj, n)
    return {'bank_id': f'X-{obj}.{n}', 'text': q, 'correct': correct, 'wrong': list(wrong), 'obj': obj,
            'explanation': why, 'review': PENDING}


def _finalise(items):
    """Place the key so positions are exactly balanced but not in a visible sequence."""
    order = sorted(range(len(items)), key=lambda i: hashlib.sha1(items[i]['bank_id'].encode()).hexdigest())
    out = [dict(q) for q in items]
    for rank, i in enumerate(order):
        q = out[i]
        k = rank % 4
        opts = list(q['wrong'])
        opts.insert(k, q['correct'])
        q['options'] = opts
        del q['wrong']
    return out


import importlib  # noqa: E402
import pkgutil  # noqa: E402

CHAPTERS = [importlib.import_module(f'{__name__}.{m.name}') for m in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name)
            if m.name.startswith('ch')]
ITSUP_CORE = {}
GLOSSARY_ADD = []
PLAN_UPDATES = {}
LABS_ADD = {}
_raw = []
for _m in CHAPTERS:
    ITSUP_CORE.update(_m.LESSONS)
    GLOSSARY_ADD += _m.GLOSSARY
    PLAN_UPDATES[_m.CHAPTER] = _m.PLAN
    LABS_ADD.update(getattr(_m, 'LABS', {}))
    _raw += _m.ITEMS
EXPANDED_CHAPTERS = sorted(PLAN_UPDATES)
EXPANSION = _finalise(_raw)
SOURCE_KEYS = sorted({k for _m in CHAPTERS for k in _m.SOURCES_USED})


def is_pending(code, chapter):
    """True for ITSUP chapters expanded in pass 9 (and the CLIENT chapters copied from them)."""
    if code == 'CLIENT':
        chapter = chapter + 7
    elif code != 'ITSUP':
        return False
    return chapter in PLAN_UPDATES
