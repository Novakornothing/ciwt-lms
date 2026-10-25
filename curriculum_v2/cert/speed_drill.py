"""Rapid-fire Port, Protocol, Acronym & Command Speed-Drill with spaced repetition (Option B pass 4).

98 high-yield recall cards in four categories, each tagged with the exams it serves (A1 = 220-1201, A2 = 220-1202,
N = N10-009). Two modes: a 60-second timed Blitz (4 options, streak counter, instant feedback, missed-card retry queue)
and Flip-Card study (Got it / Review again). Results are stored per user and card (Leitner box 1-5); the deck is
ordered so low boxes and long-unseen cards come first. Blitz distractors come from the same category and are
length-balanced so the key is never >= 1.15x the longest distractor. Pending SME review.
"""
import json
import random

from flask import abort, render_template, request
from flask_login import current_user, login_required

REVIEW = 'Pending SME review'
CATEGORIES = {
    'ports': 'Ports & Protocols',
    'specs': 'IEEE / Wi-Fi / Cable & Hardware Specs',
    'cli': 'CLI Commands (Windows, Linux, Cisco IOS)',
    'acronyms': 'Acronyms & Security/Cloud Concepts',
}
EXAM_CODES = {'T': 'FC0-U71', 'A1': '220-1201', 'A2': '220-1202', 'N': 'N10-009'}
BLITZ_SECONDS = 60
BALANCE = 1.15

_P, _S, _C, _A = 'ports', 'specs', 'cli', 'acronyms'
_RAW = [
    # ---------------------------------------------------------------- ports & protocols
    (_P, 'A1 N', 'FTP', 'TCP 20/21'), (_P, 'A1 N', 'SSH / SFTP', 'TCP 22'), (_P, 'A1 N', 'Telnet', 'TCP 23'),
    (_P, 'A1 N', 'SMTP (relay / submission)', 'TCP 25 / 587'), (_P, 'A1 N', 'DNS', 'UDP/TCP 53'),
    (_P, 'A1 N', 'DHCP (server / client)', 'UDP 67 / 68'), (_P, 'A1 N', 'TFTP', 'UDP 69'), (_P, 'A1 N', 'HTTP', 'TCP 80'),
    (_P, 'A1 N', 'Kerberos', 'TCP/UDP 88'), (_P, 'A1 N', 'POP3 / POP3S', 'TCP 110 / 995'), (_P, 'N', 'NTP', 'UDP 123'),
    (_P, 'A1 N', 'NetBIOS', 'TCP/UDP 137-139'), (_P, 'A1 N', 'IMAP / IMAPS', 'TCP 143 / 993'),
    (_P, 'A1 N', 'SNMP (polls / traps)', 'UDP 161 / 162'), (_P, 'A1 N', 'LDAP', 'TCP 389'), (_P, 'A1 N', 'HTTPS', 'TCP 443'),
    (_P, 'A1 N', 'SMB / CIFS', 'TCP 445'), (_P, 'N', 'Syslog', 'UDP 514'), (_P, 'N', 'LDAPS', 'TCP 636'),
    (_P, 'N', 'SQL Server / MySQL', 'TCP 1433 / 3306'), (_P, 'A1 N', 'RDP', 'TCP 3389'),
    (_P, 'N', 'SIP (clear / TLS)', 'UDP/TCP 5060/5061'), (_P, 'N', 'Which protocol uses TCP 22 for file transfer?', 'SFTP'),
    (_P, 'N', 'Which protocol uses UDP 514?', 'Syslog'), (_P, 'A1 N', 'Which protocol uses TCP 3389?', 'RDP'),
    (_P, 'A1 N', 'Which protocol uses TCP 445?', 'SMB'), (_P, 'N', 'Which protocol uses UDP 123?', 'NTP'),
    (_P, 'A1 N', 'Which protocol uses UDP 69?', 'TFTP'),
    # ---------------------------------------------------------------- IEEE / Wi-Fi / cable / hardware
    (_S, 'N', '802.1Q', 'VLAN tagging on trunks'), (_S, 'A2 N', '802.1X', 'Port-based network access control'),
    (_S, 'N', '802.1D / 802.1w', 'Spanning Tree / Rapid STP'), (_S, 'A1 N', '802.3af PoE', 'Up to 15.4 W per port'),
    (_S, 'A1 N', '802.3at PoE+', 'Up to 30 W per port'), (_S, 'A1 N', '802.3bt PoE++', 'Up to 60-100 W per port'),
    (_S, 'A1 N', '802.11a', '5 GHz, up to 54 Mb/s'), (_S, 'A1 N', '802.11b', '2.4 GHz, up to 11 Mb/s'),
    (_S, 'A1 N', '802.11g', '2.4 GHz, up to 54 Mb/s'), (_S, 'A1 N', '802.11n (Wi-Fi 4)', '2.4/5 GHz, MIMO, 600 Mb/s'),
    (_S, 'A1 N', '802.11ac (Wi-Fi 5)', '5 GHz only, MU-MIMO'), (_S, 'A1 N', '802.11ax (Wi-Fi 6/6E)', '2.4/5/6 GHz, OFDMA'),
    (_S, 'A1 N', 'Cat 5e', '1 Gb/s to 100 m'), (_S, 'A1 N', 'Cat 6', '10 Gb/s to 55 m'), (_S, 'A1 N', 'Cat 6A', '10 Gb/s to 100 m'),
    (_S, 'A1 N', 'Cat 8', '25/40 Gb/s to 30 m'), (_S, 'A1 N', 'T568A pins 1-2', 'White/green, green'),
    (_S, 'A1 N', 'T568B pins 1-2', 'White/orange, orange'), (_S, 'A1 N', 'LC connector', 'Small form-factor fiber latch'),
    (_S, 'A1 N', 'SC connector', 'Square push-pull fiber'), (_S, 'A1 N', 'ST connector', 'Round bayonet twist fiber'),
    (_S, 'N', 'MPO connector', 'Multi-fiber ribbon connector'), (_S, 'A1', 'USB 3.2 Gen 2x2', '20 Gb/s over USB-C'),
    (_S, 'A1', 'USB4 / Thunderbolt 4', '40 Gb/s over USB-C'), (_S, 'A1', 'PCIe 4.0 x16', 'About 32 GB/s each way'),
    (_S, 'A1', 'M.2 NVMe', 'SSD over PCIe lanes, M key'),
    # ---------------------------------------------------------------- CLI
    (_C, 'A2 N', 'ipconfig /flushdns', 'Clear the DNS resolver cache'), (_C, 'A2 N', 'netstat -ano', 'Connections with owning PID'),
    (_C, 'A2', 'sfc /scannow', 'Repair protected system files'), (_C, 'A2', 'DISM /Online /Cleanup-Image /RestoreHealth', 'Repair the Windows image store'),
    (_C, 'A2', 'gpupdate /force', 'Reapply all Group Policy now'), (_C, 'A2', 'chmod 640 file', 'Set rw-r----- permissions'),
    (_C, 'A2', 'chown alice:staff file', 'Change file owner and group'), (_C, 'A2 N', 'ss -tulpn', 'Listening sockets with process'),
    (_C, 'A2', 'journalctl -u sshd', 'Read the systemd log of a unit'), (_C, 'N', 'dig example.com MX', 'Query DNS for mail exchangers'),
    (_C, 'N', 'show vlan brief', 'VLANs and their access ports'), (_C, 'N', 'show interfaces trunk', 'Trunk ports and allowed VLANs'),
    (_C, 'N', 'show ip route', 'The router\u2019s routing table'), (_C, 'A2 N', 'tracert / traceroute', 'List each hop to a host'),
    (_C, 'A2 N', 'nslookup', 'Query a DNS server by hand'), (_C, 'A2', 'chkdsk /r', 'Find bad sectors, recover data'),
    (_C, 'A2', 'diskpart', 'Manage disks and partitions'), (_C, 'A2', 'robocopy /MIR', 'Mirror a folder tree'),
    (_C, 'A2', 'sudo', 'Run one command as root'), (_C, 'N', 'show running-config', 'Active config in RAM'),
    (_C, 'N', 'copy run start', 'Save running config to NVRAM'), (_C, 'N', 'show mac address-table', 'Learned MACs per switchport'),
    (_C, 'A2 N', 'arp -a', 'IP-to-MAC cache entries'), (_C, 'A2', 'whoami /groups', 'Your account\u2019s group SIDs'),
    # ---------------------------------------------------------------- acronyms & concepts
    (_A, 'A2 N', 'AAA', 'Authentication, authorization, accounting'), (_A, 'A2 N', 'SAML', 'XML-based federated SSO'),
    (_A, 'A2 N', 'OIDC', 'Identity layer on top of OAuth 2.0'), (_A, 'A2 N', 'RADIUS', 'UDP AAA, encrypts only password'),
    (_A, 'A2 N', 'TACACS+', 'TCP 49 AAA, encrypts full body'), (_A, 'A2 N', 'WPA3-SAE', 'Dragonfly handshake, no offline guessing'),
    (_A, 'A2 N', 'MTBF', 'Mean time between failures'), (_A, 'A2 N', 'MTTR', 'Mean time to repair/restore'),
    (_A, 'A2 N', 'RTO', 'Max time to restore a service'), (_A, 'A2 N', 'RPO', 'Max data loss measured in time'),
    (_A, 'A1 N', 'IaaS', 'You manage OS and up; VMs rented'), (_A, 'A1 N', 'PaaS', 'You manage only apps and data'),
    (_A, 'A1 N', 'SaaS', 'Provider runs the whole app'), (_A, 'A2 N', 'SPF', 'DNS list of allowed mail senders'),
    (_A, 'A2 N', 'DKIM', 'Signs mail with a domain key'), (_A, 'A2 N', 'DMARC', 'Policy when SPF/DKIM checks fail'),
    (_A, 'N', 'VLAN', 'Logical layer-2 broadcast domain'), (_A, 'N', 'VXLAN', 'Layer-2 overlay over UDP 4789'),
    (_A, 'N', 'MPLS', 'Label switching across a WAN'), (_A, 'A2 N', 'MFA', 'Two or more factor types'),
]


def _cards():
    out = []
    for n, (cat, exams, front, back) in enumerate(_RAW, 1):
        exs = exams.split()
        if ('A1' in exs or 'A2' in exs) and 'T' not in exs:
            exs = ['T'] + exs
        out.append({'id': f'SD-{n:03d}', 'cat': cat, 'exams': exs, 'front': front, 'back': back,
                    'codes': [EXAM_CODES[e] for e in exs], 'review': REVIEW})
    return out


CARDS = _cards()
BY_ID = {c['id']: c for c in CARDS}


def choices(card):
    """Key + 3 same-category distractors with the closest lengths; the key is never >= BALANCE x the longest one."""
    k = card['back']
    pool = sorted({c['back'] for c in CARDS if c['cat'] == card['cat'] and c['back'] != k},
                  key=lambda b: (abs(len(b) - len(k)), b))
    picks = pool[:3]
    if len(k) >= BALANCE * max(map(len, picks)):
        longer = [b for b in pool if len(b) * BALANCE > len(k)]
        picks = picks[:2] + longer[:1]
    opts = picks + [k]
    random.Random(card['id']).shuffle(opts)
    return opts


def balance_violations():
    out = []
    for c in CARDS:
        opts = choices(c)
        wrong = [o for o in opts if o != c['back']]
        if len(c['back']) >= BALANCE * max(map(len, wrong)):
            out.append(c['id'])
    return out


def deck(exam=None, cat=None):
    return [c for c in CARDS if (not exam or exam in c['exams']) and (not cat or c['cat'] == cat)]


def register(app, db, deps):
    """deps: ClassSection, Enrollment, utcnow."""
    ClassSection, Enrollment, utcnow = deps['ClassSection'], deps['Enrollment'], deps['utcnow']

    class SpeedDrillStat(db.Model):
        __tablename__ = 'speed_drill_stat'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        card_id = db.Column(db.String(12), nullable=False)
        box = db.Column(db.Integer, default=1)          # Leitner box 1 (review soon) .. 5 (known)
        seen = db.Column(db.Integer, default=0)
        right = db.Column(db.Integer, default=0)
        best_streak = db.Column(db.Integer, default=0)
        updated_at = db.Column(db.DateTime)
        __table_args__ = (db.UniqueConstraint('user_id', 'card_id', name='uq_speed_drill_user_card'),)

    with app.app_context():
        SpeedDrillStat.__table__.create(db.engine, checkfirst=True)

    def section(section_id):
        sec = db.get_or_404(ClassSection, section_id)
        if current_user.role in ('admin', 'instructor'):
            return sec
        if not Enrollment.query.filter_by(user_id=current_user.id, section_id=sec.id).first():
            abort(403)
        return sec

    @login_required
    def speed_drill(section_id):
        sec = section(section_id)
        exam = request.args.get('exam') if request.args.get('exam') in EXAM_CODES else ''
        cat = request.args.get('cat') if request.args.get('cat') in CATEGORIES else ''
        stats = {s.card_id: s for s in SpeedDrillStat.query.filter_by(user_id=current_user.id).all()}
        cards = deck(exam, cat)
        # spaced repetition: lowest box first, then fewest seen; shuffled within ties
        rng = random.Random()
        cards = sorted(cards, key=lambda c: ((stats[c['id']].box if c['id'] in stats else 0),
                                             (stats[c['id']].seen if c['id'] in stats else 0), rng.random()))
        payload = [{'id': c['id'], 'cat': CATEGORIES[c['cat']], 'front': c['front'], 'back': c['back'],
                    'codes': c['codes'], 'choices': choices(c),
                    'box': stats[c['id']].box if c['id'] in stats else 0} for c in cards]
        known = sum(1 for s in stats.values() if s.box >= 4)
        return render_template('exam_sim/speed_drill.html', section=sec, cards=payload, exam=exam, cat=cat,
                               categories=CATEGORIES, exams=EXAM_CODES, seconds=BLITZ_SECONDS, review=REVIEW,
                               known=known, seen=len(stats), total=len(CARDS),
                               best=max((s.best_streak or 0 for s in stats.values()), default=0))

    @login_required
    def speed_drill_record(section_id):
        section(section_id)
        data = request.get_json(silent=True) or request.form
        card = BY_ID.get(data.get('card'))
        result = data.get('result')
        if not card or result not in ('right', 'wrong', 'got', 'again'):
            abort(400)
        s = SpeedDrillStat.query.filter_by(user_id=current_user.id, card_id=card['id']).first()
        if not s:
            s = SpeedDrillStat(user_id=current_user.id, card_id=card['id'], box=1, seen=0, right=0, best_streak=0)
            db.session.add(s)
        ok = result in ('right', 'got')
        s.seen = (s.seen or 0) + 1
        s.right = (s.right or 0) + int(ok)
        s.box = min(5, (s.box or 1) + 1) if ok else 1
        try:
            streak = int(data.get('streak') or 0)
        except (TypeError, ValueError):
            streak = 0
        s.best_streak = max(s.best_streak or 0, min(streak, 999))
        s.updated_at = utcnow()
        db.session.commit()
        return {'ok': True, 'card': card['id'], 'box': s.box, 'seen': s.seen, 'right': s.right}

    app.add_url_rule('/student/section/<int:section_id>/speed-drill', 'speed_drill', speed_drill, methods=['GET'])
    app.add_url_rule('/student/section/<int:section_id>/speed-drill/record', 'speed_drill_record', speed_drill_record,
                     methods=['POST'])
    return SpeedDrillStat
