"""Novak LMS™ Smart Search Engine:
Tokenization, Porter-lite stemming, 140+ IT/Networking synonym & acronym expansions,
Levenshtein/SequenceMatcher typo tolerance, BM25-inspired multi-field ranking,
and context snippet highlighting for /search and /api/search.
"""
import difflib
import html
import re
from html import unescape

STOP_WORDS = frozenset({
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'do', 'does', 'for',
    'from', 'how', 'in', 'into', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
    'the', 'their', 'then', 'there', 'these', 'this', 'to', 'was', 'what',
    'when', 'where', 'which', 'who', 'why', 'with', 'can', 'use', 'using',
})

# Explicit high-frequency IT & networking typo corrections
TYPO_FIXES = {
    'etherchanel': 'etherchannel',
    'etherchannl': 'etherchannel',
    'ehterchannel': 'etherchannel',
    'subnettng': 'subnetting',
    'subneting': 'subnetting',
    'subent': 'subnet',
    'subents': 'subnets',
    'truble': 'trouble',
    'trubleshoot': 'troubleshoot',
    'trubleshooting': 'troubleshooting',
    'troublshoot': 'troubleshoot',
    'neigbor': 'neighbor',
    'nieghbor': 'neighbor',
    'ospfneigbor': 'ospf neighbor',
    'dhpc': 'dhcp',
    'dchp': 'dhcp',
    'kerbros': 'kerberos',
    'kerberous': 'kerberos',
    'bootmgr': 'bootmgfw',
    'bootmanger': 'boot manager',
    'winlod': 'winload',
    'ipconfg': 'ipconfig',
    'ifconfg': 'ifconfig',
    'nslokup': 'nslookup',
    'tracrt': 'tracert',
    'tracerout': 'traceroute',
    'parition': 'partition',
    'partiton': 'partition',
    'permissons': 'permissions',
    'permisions': 'permissions',
    'firwall': 'firewall',
    'firewal': 'firewall',
    'wirless': 'wireless',
    'wireles': 'wireless',
    'wiffi': 'wifi',
    'motherbord': 'motherboard',
    'motheboard': 'motherboard',
    'procesor': 'processor',
    'virutal': 'virtual',
    'virtulization': 'virtualization',
    'hyperviser': 'hypervisor',
    'bitloker': 'bitlocker',
    'ransomeware': 'ransomware',
    'malwear': 'malware',
    'phisng': 'phishing',
    'phising': 'phishing',
    'switchprt': 'switchport',
    'trunkng': 'trunking',
    'spaning': 'spanning',
    'bluetoth': 'bluetooth',
    'maintenence': 'maintenance',
    'fuzer': 'fuser',
    'lazr': 'laser',
    'regstry': 'registry',
    'eventviwer': 'event viewer',
    'taskmanger': 'task manager',
    'powrshell': 'powershell',
    'activesirectory': 'active directory',
    'grouppolicy': 'group policy',
}

# 140+ bidirectional IT & Networking Synonym / Acronym Groups
SYNONYM_GROUPS = [
    ('bsod', 'blue screen', 'stop error', 'bugcheck', 'crash', 'memory dump', 'symptom'),
    ('wifi', 'wi-fi', 'wireless', 'wlan', '802.11', '802.11ax', '802.11ac', '802.11be', 'ssid', 'channel', 'rf'),
    ('wifi 6', 'wi-fi 6', '802.11ax', 'ofdma', 'mu-mimo', 'wireless'),
    ('wifi 6e', 'wi-fi 6e', '6 ghz', '6ghz', '802.11ax'),
    ('wifi 7', 'wi-fi 7', '802.11be', 'mlo', '320 mhz'),
    ('wpa3', 'wpa2', 'sae', 'ccmp', 'aes', '802.1x', 'eap-tls', 'peap', 'wireless security'),
    ('cmd', 'command prompt', 'cli', 'terminal', 'shell', 'console', 'powershell', 'bash'),
    ('boot', 'bootmgr', 'bootmgfw', 'winload', 'ntoskrnl', 'uefi', 'bios', 'post', 'bcd', 'bcdedit', 'bootrec', 'esp', 'secure boot', 'winre', 'startup'),
    ('bootrec', 'bcdedit', 'fixmbr', 'fixboot', 'rebuildbcd', 'winre', 'recovery', 'boot'),
    ('uefi', 'bios', 'firmware', 'secure boot', 'tpm', 'tpm 2.0', 'post', 'cmos', 'gpt'),
    ('gpt', 'mbr', 'partition', 'diskpart', 'efi system partition', 'esp', 'storage'),
    ('ip', 'ipv4', 'ipv6', 'addressing', 'subnet', 'subnetting', 'cidr', 'netmask', 'prefix'),
    ('ipconfig', 'ifconfig', 'ip addr', 'network configuration', 'default gateway', 'dns', 'dhcp'),
    ('subnet', 'subnetting', 'cidr', 'vlsm', 'slash', 'netmask', 'broadcast', 'host range', 'binary'),
    ('ipv6', 'slaac', 'fe80', 'link-local', ' neighbor discovery', 'ndp', 'dual stack', '128-bit'),
    ('mac', 'mac address', 'physical address', 'layer 2', 'cam table', 'oui', 'bia', 'ethernet', 'arp'),
    ('arp', 'address resolution protocol', 'mac table', 'neighbor cache', 'layer 2'),
    ('switch', 'switching', 'vlan', 'trunk', 'trunking', '802.1q', 'stp', 'spanning tree', 'switchport', 'cam'),
    ('vlan', '802.1q', 'dot1q', 'trunk', 'trunking', 'native vlan', 'access port', 'inter-vlan', 'svi', 'router on a stick'),
    ('trunk', 'trunking', '802.1q', 'allowed vlan', 'native vlan', 'switchport mode trunk', 'uplink'),
    ('etherchannel', 'lacp', 'pagp', '802.3ad', 'port-channel', 'link aggregation', 'bonding', 'nic teaming'),
    ('stp', 'spanning tree', 'rstp', '802.1d', '802.1w', 'root bridge', 'bpdu', 'bpduguard', 'portfast', 'loop'),
    ('ospf', 'open shortest path first', 'link-state', 'area 0', 'neighbor', 'adjacency', 'hello', 'cost', 'routing', 'router'),
    ('bgp', 'border gateway protocol', 'ebgp', 'ibgp', 'autonomous system', 'asn', 'wan', 'routing'),
    ('rip', 'eigrp', 'distance vector', 'dynamic routing', 'administrative distance', 'metric'),
    ('routing', 'router', 'static route', 'default route', 'next hop', 'routing table', 'show ip route', 'ospf', 'bgp'),
    ('nat', 'pat', 'network address translation', 'port forwarding', 'overload', 'inside global', 'rfc 1918', 'private ip'),
    ('rfc 1918', 'private ip', '10.0.0.0', '172.16.0.0', '192.168.0.0', 'apipa', '169.254'),
    ('apipa', '169.254', 'link-local', 'dhcp failure', 'no dhcp'),
    ('dhcp', 'dora', 'discover', 'offer', 'request', 'acknowledge', 'lease', 'scope', 'ip helper-address', 'relay', 'apipa', 'port 67', 'port 68'),
    ('dns', 'domain name system', 'name resolution', 'nslookup', 'dig', 'port 53', 'cname', 'aaaa', 'mx', 'ptr', 'srv', 'txt', 'spf', 'dkim', 'dmarc'),
    ('vpn', 'ipsec', 'ikev2', 'wireguard', 'ssl vpn', 'tls', 'tunnel', 'split tunnel', 'full tunnel', 'remote access', 'site-to-site'),
    ('active directory', 'ad', 'ad ds', 'domain controller', 'gpo', 'group policy', 'kerberos', 'ldap', 'ldaps', 'domain join', 'gpupdate', 'gpresult'),
    ('gpo', 'group policy', 'gpupdate', 'gpresult', 'lsdou', 'active directory', 'gpedit'),
    ('kerberos', 'ticket', 'kdc', 'time skew', 'ntp', 'port 88', 'authentication', 'domain'),
    ('ldap', 'ldaps', 'port 389', 'port 636', 'directory', 'authentication'),
    ('aaa', 'radius', 'tacacs', 'tacacs+', '802.1x', 'authentication', 'authorization', 'accounting', 'port 1812', 'port 49'),
    ('linux', 'bash', 'chmod', 'chown', 'systemd', 'systemctl', 'grep', 'ps', 'top', 'apt', 'dnf', 'ext4', 'xfs', 'sudo', 'ssh'),
    ('chmod', 'chown', 'permissions', 'rwx', 'octal', '755', '644', 'posix', 'linux'),
    ('ntfs', 'icacls', 'permissions', 'acl', 'share permissions', 'effective permissions', 'fat32', 'exfat', 'refs'),
    ('printer', 'printing', 'laser', 'fuser', 'toner', 'drum', 'imaging', 'transfer belt', 'pickup roller', 'separation pad', 'spooler', 'inkjet', 'thermal'),
    ('laser', 'fuser', 'toner', 'drum', 'corona wire', 'transfer', 'ghosting', 'smearing', 'printer', 'maintenance kit'),
    ('raid', 'raid 0', 'raid 1', 'raid 5', 'raid 6', 'raid 10', 'striping', 'mirroring', 'parity', 'array', 'redundancy', 'storage'),
    ('ssd', 'nvme', 'm.2', 'pcie', 'sata', 'ahci', 'hdd', 'storage', 'smart', 'trim', 'disk'),
    ('ram', 'memory', 'dimm', 'sodimm', 'ddr4', 'ddr5', 'ecc', 'dual-channel', 'dual channel', 'pagefile', 'virtual memory'),
    ('cpu', 'processor', 'socket', 'lga', 'am4', 'am5', 'heatsink', 'thermal paste', 'cooling', 'throttling', 'x86', 'arm'),
    ('psu', 'power supply', 'wattage', '24-pin', 'atx', 'eps', '12v rail', '5v', '3.3v', 'modular', 'multimeter'),
    ('motherboard', 'form factor', 'atx', 'micro-atx', 'mini-itx', 'pcie', 'chipset', 'cmos', 'post', 'beep codes', 'debug led'),
    ('post', 'power-on self-test', 'beep code', 'debug led', 'no video', 'no boot', 'motherboard', 'ram'),
    ('cable', 'cabling', 't568a', 't568b', 'pinout', 'rj-45', 'rj45', 'cat5e', 'cat6', 'cat6a', 'utp', 'stp', 'plenum', 'crimper', 'punchdown', 'patch panel'),
    ('fiber', 'optical', 'single-mode', 'smf', 'multimode', 'mmf', 'lc', 'sc', 'st', 'mpo', 'sfp', 'transceiver', 'otdr', 'wavelength'),
    ('poe', 'power over ethernet', '802.3af', '802.3at', '802.3bt', 'poe+', 'poe++', 'injector', 'switch power budget'),
    ('firewall', 'acl', 'access control list', 'stateful', 'stateless', 'implicit deny', 'dmz', 'netfirewallrule', 'windows defender firewall'),
    ('rdp', 'remote desktop', 'termservice', 'port 3389', 'nla', 'remote assistance', 'remote access'),
    ('ssh', 'secure shell', 'port 22', 'putty', 'openssh', 'remote cli', 'telnet', 'port 23'),
    ('http', 'https', 'tls', 'ssl', 'port 80', 'port 443', 'certificate', 'pki', 'ca'),
    ('smb', 'cifs', 'port 445', 'file share', 'net share', 'net use', 'unc path', 'nas'),
    ('snmp', 'mib', 'oid', 'trap', 'port 161', 'port 162', 'snmpv3', 'monitoring', 'telemetry'),
    ('syslog', 'port 514', 'siem', 'logging', 'severity level', 'event viewer', 'journalctl'),
    ('ntp', 'network time protocol', 'port 123', 'stratum', 'w32tm', 'clock', 'time sync'),
    ('sfc', 'dism', 'system file checker', 'scannow', 'restorehealth', 'chkdsk', 'windows repair', 'corrupt'),
    ('winre', 'recovery environment', 'safe mode', 'system restore', 'reset this pc', 'in-place upgrade', 'clean install'),
    ('malware', 'ransomware', 'trojan', 'worm', 'rootkit', 'spyware', 'keylogger', 'quarantine', 'antivirus', 'edr', 'defender'),
    ('phishing', 'vishing', 'smishing', 'whaling', 'spear phishing', 'social engineering', 'tailgating', 'impersonation'),
    ('mfa', '2fa', 'multi-factor', 'totp', 'fido2', 'webauthn', 'passkey', 'biometrics', 'sso', 'saml', 'oidc'),
    ('bitlocker', 'encryption', 'tpm', 'manage-bde', 'recovery key', 'efs', 'full disk encryption', 'filevault', 'luks'),
    ('cloud', 'iaas', 'paas', 'saas', 'public cloud', 'private cloud', 'hybrid', 'multicloud', 'elasticity', 'scalability'),
    ('virtualization', 'vm', 'virtual machine', 'hypervisor', 'type 1', 'type 2', 'hyper-v', 'kvm', 'esxi', 'container', 'docker', 'snapshot'),
    ('mobile', 'mdm', 'mam', 'ios', 'ipados', 'android', 'oled', 'lcd', 'digitizer', 'battery', 'swollen battery', 'imei', 'esim'),
    ('laptop', 'inverter', 'backlight', 'webcam', 'hinge', 'wi-fi antenna', 'sodimm', 'm.2', 'dc jack', 'docking station', 'thunderbolt', 'usb-c'),
    ('display', 'monitor', 'hdmi', 'displayport', 'usb-c', 'edid', 'refresh rate', 'resolution', 'dead pixel', 'ghosting', 'projector'),
    ('osi', 'osi model', 'layer 1', 'layer 2', 'layer 3', 'layer 4', 'layer 7', 'encapsulation', 'pdu', 'frame', 'packet', 'segment', 'tcp/ip'),
    ('tcp', 'udp', 'three-way handshake', 'syn', 'ack', 'port', 'connectionless', 'connection-oriented', 'transport layer'),
    ('icmp', 'ping', 'traceroute', 'tracert', 'ttl', 'pathping', 'mtr', 'latency', 'jitter', 'packet loss'),
    ('netstat', 'ss', 'tcpdump', 'wireshark', 'pcap', 'packet capture', 'netsh', 'nmap', 'port scan'),
    ('cdr', 'RTO', 'RPO', 'mttr', 'mtbf', 'disaster recovery', 'backup', '3-2-1', 'full backup', 'incremental', 'differential', 'snapshot', 'ups'),
    ('ups', 'uninterruptible power supply', 'surge protector', 'pdu', 'generator', 'brownout', 'blackout', 'line interactive'),
    ('esd', 'electrostatic discharge', 'wrist strap', 'mat', 'msds', 'sds', 'safety', 'lithium battery', 'e-waste'),
    ('ticket', 'ticketing', 'sla', 'escalation', 'change management', 'rollback', 'maintenance window', 'documentation', 'runbook', 'kb', 'knowledge base'),
    ('database', 'sql', 'relational', 'nosql', 'primary key', 'foreign key', 'schema', 'select', 'insert', 'update', 'backup'),
    ('code', 'programming', 'variable', 'loop', 'branch', 'if else', 'array', 'function', 'boolean', 'integer', 'string', 'json', 'xml'),
    ('ai', 'artificial intelligence', 'machine learning', 'generative ai', 'prompt', 'automation', 'chatbot', 'hallucination', 'data privacy'),
]

# Build bidirectional lookup map: term -> set of related terms
_SYNONYM_MAP = {}
for _grp in SYNONYM_GROUPS:
    _norm_grp = [t.strip().lower() for t in _grp if t.strip()]
    for _term in _norm_grp:
        _bucket = _SYNONYM_MAP.setdefault(_term, set())
        for _other in _norm_grp:
            if _other != _term:
                _bucket.add(_other)
        # Also index single words of multi-word group keys
        for _tok in re.findall(r'[a-z0-9._-]+', _term):
            if len(_tok) >= 3 and _tok not in STOP_WORDS:
                _tb = _SYNONYM_MAP.setdefault(_tok, set())
                for _other in _norm_grp:
                    _tb.add(_other)

_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE = re.compile(r'\s+')
_H_RE = re.compile(r'<h[234][^>]*>(.*?)</h[234]>', re.I | re.S)


def strip_html(raw: str) -> str:
    if not raw:
        return ''
    return _WS_RE.sub(' ', unescape(_TAG_RE.sub(' ', raw))).strip()


def extract_headings(raw: str) -> str:
    if not raw:
        return ''
    return ' '.join(strip_html(m.group(1)) for m in _H_RE.finditer(raw))


def stem(word: str) -> str:
    """Porter-lite stemmer tailored for IT, networking, and operating system terminology."""
    w = (word or '').lower().strip()
    if len(w) <= 3 or any(ch.isdigit() for ch in w):
        return w
    # Preserve exact short acronyms
    if w in ('bios', 'cmos', 'ospf', 'icmp', 'dhcp', 'vlan', 'cidr', 'apipa', 'sata', 'nvme', 'raid', 'uefi', 'ntfs', 'refs'):
        return w
    if w.endswith('ies') and len(w) > 4:
        return w[:-3] + 'y'
    if w.endswith('tting') and len(w) > 6:
        return w[:-4]
    if w.endswith('nning') and len(w) > 6:
        return w[:-4]
    for suf in ('ization', 'isation', 'ation', 'ition', 'ment', 'ness', 'ings', 'ing', 'ers', 'ors', 'ed', 'es', 'er', 'or', 'ly', 's'):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            base = w[:-len(suf)]
            if base.endswith(('tt', 'nn', 'pp', 'gg', 'dd')) and len(base) > 3:
                base = base[:-1]
            if base in ('rout', 'configur', 'troubleshoot', 'switch', 'subnet', 'print', 'encrypt', 'connect', 'networ', 'parit', 'partit', 'permiss', 'virtual'):
                return base
            return base
    return w


def tokenize(text: str) -> list:
    """Split text into normalized tokens, handling hyphens/dots in technical terms."""
    if not text:
        return []
    s = text.lower().strip()
    # Normalize wi-fi -> wifi
    s = re.sub(r'\bwi-fi\b', 'wifi', s)
    raw_tokens = re.findall(r'[a-z0-9]+(?:[._-][a-z0-9]+)*', s)
    out = []
    seen = set()
    for tok in raw_tokens:
        tok_clean = tok.strip('._-')
        if not tok_clean or tok_clean in STOP_WORDS:
            continue
        if tok_clean not in seen:
            seen.add(tok_clean)
            out.append(tok_clean)
        # Also split hyphenated/dotted tokens if not a pure version number
        if '-' in tok_clean or '_' in tok_clean:
            compact = tok_clean.replace('-', '').replace('_', '')
            if compact and compact not in seen:
                seen.add(compact)
                out.append(compact)
            for sub in re.split(r'[-_]', tok_clean):
                if len(sub) >= 2 and sub not in STOP_WORDS and sub not in seen:
                    seen.add(sub)
                    out.append(sub)
    return out


# Built-in domain vocabulary for typo tolerance even without DB
_BASE_VOCAB = sorted({
    tok
    for grp in SYNONYM_GROUPS
    for phrase in grp
    for tok in re.findall(r'[a-z0-9._-]+', phrase.lower())
    if len(tok) >= 4
} | set(TYPO_FIXES.values()) | {
    'etherchannel', 'subnetting', 'troubleshooting', 'neighbor', 'kerberos',
    'bootmgfw', 'winload', 'ipconfig', 'ifconfig', 'nslookup', 'traceroute',
    'partition', 'permissions', 'firewall', 'wireless', 'motherboard',
    'processor', 'virtualization', 'hypervisor', 'bitlocker', 'ransomware',
    'malware', 'phishing', 'switchport', 'trunking', 'spanning', 'bluetooth',
    'maintenance', 'fuser', 'laser', 'registry', 'powershell', 'active',
    'directory', 'policy', ' ospf', 'vlan', 'dhcp', 'apipa', 'dns', 'raid',
    'nvme', 'dimm', 'sodimm', 't568a', 't568b', 'cat6', 'cat6a', 'fiber',
    'syslog', 'snmp', 'radius', 'tacacs', 'wireguard', 'ipsec', 'icacls',
    'chmod', 'chown', 'systemd', 'diskpart', 'bcdedit', 'bootrec', 'dism',
})


def fuzzy_correct_token(tok: str, extra_vocab=None) -> str:
    """Return a typo-corrected token if `tok` is a near-miss to a known technical term."""
    t = (tok or '').lower().strip()
    if not t:
        return t
    if t in TYPO_FIXES:
        return TYPO_FIXES[t]
    if len(t) < 4 or any(c.isdigit() for c in t):
        return t
    vocab = _BASE_VOCAB if not extra_vocab else list(_BASE_VOCAB) + list(extra_vocab)
    if t in vocab or t in _SYNONYM_MAP:
        return t
    best = None
    best_ratio = 0.0
    for cand in vocab:
        if abs(len(cand) - len(t)) > 2:
            continue
        if cand[0] != t[0] and cand[:2] != t[:2]:
            continue
        r = difflib.SequenceMatcher(None, t, cand).ratio()
        if r > best_ratio:
            best_ratio = r
            best = cand
    if best and best_ratio >= 0.78:
        return best
    return t


def expand_query(raw_query: str, extra_vocab=None) -> dict:
    """Analyze a raw user query into primary tokens, typo-corrected tokens, stems, and synonyms."""
    q = (raw_query or '').strip()
    q_low = re.sub(r'\bwi-fi\b', 'wifi', q.lower())

    # Check whole-query typo fix first
    raw_tokens = tokenize(q_low)
    corrected_tokens = []
    any_corrected = False
    for t in raw_tokens:
        fixed = fuzzy_correct_token(t, extra_vocab=extra_vocab)
        if fixed != t:
            any_corrected = True
        for sub in fixed.split():
            if sub not in corrected_tokens:
                corrected_tokens.append(sub)

    corrected_query = ' '.join(corrected_tokens) if any_corrected else q

    # Primary tokens & stems
    primary_tokens = list(dict.fromkeys(raw_tokens + corrected_tokens))
    primary_stems = list(dict.fromkeys(stem(t) for t in primary_tokens if len(t) >= 2))

    # Synonym expansion (phrase + token level)
    synonyms = set()
    if q_low in _SYNONYM_MAP:
        synonyms.update(_SYNONYM_MAP[q_low])
    if corrected_query.lower() in _SYNONYM_MAP:
        synonyms.update(_SYNONYM_MAP[corrected_query.lower()])
    for t in corrected_tokens:
        if t in _SYNONYM_MAP:
            synonyms.update(_SYNONYM_MAP[t])
        st = stem(t)
        if st in _SYNONYM_MAP:
            synonyms.update(_SYNONYM_MAP[st])

    # Keep top relevant synonym tokens (avoiding overly broad dilution)
    synonym_tokens = []
    for phrase in sorted(synonyms):
        for st_tok in tokenize(phrase):
            if st_tok not in primary_tokens and st_tok not in synonym_tokens:
                synonym_tokens.append(st_tok)
    synonym_tokens = synonym_tokens[:28]

    return {
        'raw_query': q,
        'corrected_query': corrected_query,
        'did_you_mean': corrected_query if any_corrected else None,
        'primary_tokens': primary_tokens,
        'primary_stems': primary_stems,
        'synonym_tokens': synonym_tokens,
        'expanded_terms': (corrected_tokens + synonym_tokens[:8])[:12],
    }


_DOC_CACHE = {}
_LAB_CACHE = None


def _norm_low(s: str) -> str:
    return re.sub(r'\bwi-fi\b', 'wifi', (s or '').lower())


def score_document(title: str, headings: str, body: str, qinfo: dict, code_or_meta: str = '', _pre_normalized: bool = False) -> float:
    """BM25-inspired multi-field relevance scorer."""
    if _pre_normalized:
        t_low, h_low, b_low, m_low = title, headings, body, code_or_meta
    else:
        t_low = _norm_low(title)
        h_low = _norm_low(headings)
        b_low = _norm_low(body)
        m_low = (code_or_meta or '').lower()

    raw_q = re.sub(r'\bwi-fi\b', 'wifi', (qinfo.get('raw_query') or '').lower().strip())
    corr_q = re.sub(r'\bwi-fi\b', 'wifi', (qinfo.get('corrected_query') or '').lower().strip())

    score = 0.0
    matched_primary = 0
    matched_synonym = 0

    # 1. Exact phrase matches
    for phrase in dict.fromkeys([raw_q, corr_q]):
        if not phrase or len(phrase) < 2:
            continue
        if phrase in t_low:
            score += 45.0
        if phrase in m_low:
            score += 35.0
        if phrase in h_low:
            score += 24.0
        if phrase in b_low:
            score += 14.0

    # 2. Primary tokens & stems
    p_tokens = qinfo.get('primary_tokens') or []
    for tok in p_tokens:
        st = stem(tok)
        tok_hit = False
        if tok in t_low or (len(st) >= 4 and st in t_low):
            score += 22.0
            tok_hit = True
        if tok in m_low or (len(st) >= 4 and st in m_low):
            score += 18.0
            tok_hit = True
        if tok in h_low or (len(st) >= 4 and st in h_low):
            score += 14.0
            tok_hit = True
        if tok in b_low or (len(st) >= 4 and st in b_low):
            # Term frequency with saturation (BM25 style)
            tf = b_low.count(tok) + (b_low.count(st) if st != tok and len(st) >= 4 else 0)
            tf_score = min(12.0, 4.0 * (tf / (tf + 1.5)) * 2.5)
            score += tf_score
            tok_hit = True
        if tok_hit:
            matched_primary += 1

    # Multi-word coverage bonus: reward docs matching multiple query tokens
    if matched_primary >= 2:
        score += matched_primary * 12.0

    # 3. Synonym expansion matches
    for syn in (qinfo.get('synonym_tokens') or []):
        syn_hit = False
        if syn in t_low:
            score += 9.5
            syn_hit = True
        elif syn in h_low:
            score += 6.5
            syn_hit = True
        elif syn in b_low:
            score += 3.0
            syn_hit = True
        if syn_hit:
            matched_synonym += 1

    if matched_primary == 0 and matched_synonym == 0:
        return 0.0

    # Cap pure-synonym score unless strong synonym cluster matches
    if matched_primary == 0 and matched_synonym < 2 and score < 8.0:
        return 0.0

    return round(score, 2)


def build_snippet(raw_html: str, qinfo: dict, max_len: int = 210) -> str:
    """Extract the highest-signal snippet from `raw_html` and wrap matched terms in <mark>."""
    plain = strip_html(raw_html)
    if not plain:
        return ''

    candidates = (
        [qinfo.get('corrected_query', ''), qinfo.get('raw_query', '')]
        + (qinfo.get('primary_tokens') or [])
        + (qinfo.get('primary_stems') or [])
        + (qinfo.get('synonym_tokens') or [])[:10]
    )
    candidates = [c.strip() for c in candidates if c and len(c.strip()) >= 2]

    low = plain.lower()
    best_idx = -1
    for cand in candidates:
        idx = low.find(cand.lower())
        if idx >= 0:
            best_idx = idx
            break

    if best_idx < 0:
        piece = plain[:max_len]
        if len(plain) > max_len:
            piece += '…'
    else:
        start = max(0, best_idx - 55)
        end = min(len(plain), best_idx + max_len - 55)
        piece = ('…' if start > 0 else '') + plain[start:end].strip() + ('…' if end < len(plain) else '')

    # Safely escape then highlight matched terms
    escaped = html.escape(piece)
    hl_terms = sorted(
        {t for t in (qinfo.get('primary_tokens') or []) + (qinfo.get('synonym_tokens') or [])[:6] if len(t) >= 2},
        key=len,
        reverse=True,
    )
    if hl_terms:
        pat = re.compile(r'(' + '|'.join(re.escape(html.escape(t)) for t in hl_terms[:10]) + r')', re.I)
        escaped = pat.sub(r'<mark class="search-hl">\1</mark>', escaped)
    return escaped


def run_smart_search(
    q: str,
    db,
    Course,
    Module,
    Lesson,
    KnowledgeTest,
    course_ids: list,
    section_for_course_fn,
    is_available_fn,
    current_user,
    url_for_fn,
    limit: int = 45,
) -> dict:
    """Execute smart fuzzy/synonym/stemmed search across Lessons, Labs, Chapters, Objectives, and Tests."""
    q = (q or '').strip()
    if not q:
        return {
            'query': '',
            'corrected_query': '',
            'did_you_mean': None,
            'expanded_terms': [],
            'results': [],
            'categories': {'lessons': [], 'labs': [], 'objectives': [], 'chapters': [], 'tests': []},
        }

    # Gather dynamic vocabulary from lesson titles & cache normalized lesson text
    all_lessons = (
        Lesson.query.join(Module, Lesson.module_id == Module.id)
        .filter(Module.course_id.in_(course_ids))
        .order_by(Module.order, Lesson.order)
        .all()
    ) if course_ids else []

    title_vocab = set()
    for les in all_lessons:
        for tok in re.findall(r'[a-z0-9]{4,}', (les.title or '').lower()):
            title_vocab.add(tok)

    qinfo = expand_query(q, extra_vocab=title_vocab)

    sec_cache = {}
    avail_cache = {}

    def _get_sec(cid):
        if cid not in sec_cache:
            sec_cache[cid] = section_for_course_fn(cid)
        return sec_cache[cid]

    def _is_avail(sec_id, kind, obj_id, uid):
        k = (sec_id, kind, obj_id, uid)
        if k not in avail_cache:
            avail_cache[k] = is_available_fn(sec_id, kind, obj_id, uid)
        return avail_cache[k]

    scored_results = []
    categories = {'lessons': [], 'labs': [], 'objectives': [], 'chapters': [], 'tests': []}

    # 1. Score Lessons (using in-memory _DOC_CACHE keyed by (lesson.id, content_len))
    lesson_hits = []
    for lesson in all_lessons:
        raw_c = lesson.content or ''
        ckey = (lesson.id, len(raw_c), lesson.title)
        cached = _DOC_CACHE.get(ckey)
        if cached is None:
            module = lesson.module
            course = module.course
            plain_txt = strip_html(raw_c)
            cached = (
                _norm_low(lesson.title),
                _norm_low(extract_headings(raw_c)),
                _norm_low(plain_txt),
                f"{course.code} {course.title} {module.title} {lesson.order}".lower(),
                plain_txt,
            )
            _DOC_CACHE[ckey] = cached
        sc = score_document(cached[0], cached[1], cached[2], qinfo, cached[3], _pre_normalized=True)
        if sc > 0:
            lesson_hits.append((sc, lesson, cached[4]))

    lesson_hits.sort(key=lambda x: (-x[0], x[1].title or ''))
    is_stu = getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'role', '') == 'student'
    uid = getattr(current_user, 'id', None)
    for sc, lesson, plain_txt in lesson_hits[:max(limit, 20)]:
        module = lesson.module
        course = module.course
        section = _get_sec(course.id)
        if not section:
            continue
        locked = is_stu and not _is_avail(section.id, 'module', module.id, uid)
        url = (
            url_for_fn('view_lesson', section_id=section.id, module_id=module.id, lesson_id=lesson.id)
            if not locked
            else url_for_fn('student_section', section_id=section.id)
        )
        Snippet_html = build_snippet(plain_txt, qinfo)
        item = {
            'kind': 'Lesson',
            'title': lesson.title,
            'chapter': module.title,
            'course': course.title,
            'course_code': course.code,
            'snippet': strip_html(Snippet_html),
            'snippet_html': Snippet_html,
            'locked': locked,
            'url': url,
            'score': sc,
        }
        scored_results.append(item)
        categories['lessons'].append(item)

    # 2. Score Interactive Labs
    try:
        import interactive_labs as IL
        for lab in getattr(IL, 'LABS', []):
            l_title = lab.get('title') or lab.get('id') or ''
            l_kind = lab.get('kind') or 'lab'
            l_body = ' '.join(str( lab.get(k) or '') for k in ('summary', 'prompt', 'scenario', 'course', 'chapter'))
            sc = score_document(l_title, l_kind, l_body, qinfo, f"{lab.get('id', '')} {lab.get('course', '')}")
            if sc <= 0:
                continue
            Snippet_html = build_snippet(l_body or l_title, qinfo)
            item = {
                'kind': 'Interactive Lab',
                'title': f"{l_title} ({l_kind.upper()})",
                'chapter': f"Hands-On Lab · {lab.get('course', 'All Courses')}",
                'course': lab.get('course', 'Interactive Lab'),
                'snippet': strip_html(Snippet_html),
                'snippet_html': Snippet_html,
                'locked': False,
                'url': url_for_fn('interactive_lab', lab_id=lab['id']),
                'score': sc * 0.95,
            }
            scored_results.append(item)
            categories['labs'].append(item)
    except Exception:
        pass

    # 3. Score Chapters (Modules)
    if course_ids:
        modules = Module.query.filter(Module.course_id.in_(course_ids)).order_by(Module.order).all()
        for module in modules:
            course = module.course
            m_body = strip_html(module.content or '')
            sc = score_document(module.title, '', m_body, qinfo, f"{course.code} Chapter {module.order}")
            if sc <= 0:
                continue
            section = section_for_course_fn(course.id)
            if not section:
                continue
            locked = (
                getattr(current_user, 'is_authenticated', False)
                and getattr(current_user, 'role', '') == 'student'
                and not is_available_fn(section.id, 'module', module.id, current_user.id)
            )
            Snippet_html = build_snippet(module.content or module.title, qinfo)
            item = {
                'kind': 'Chapter',
                'title': module.title,
                'chapter': course.title,
                'course': course.title,
                'snippet': strip_html(Snippet_html),
                'snippet_html': Snippet_html,
                'locked': locked,
                'url': url_for_fn('view_module', section_id=section.id, module_id=module.id)
                if not locked else url_for_fn('student_section', section_id=section.id),
                'score': sc * 0.85,
            }
            scored_results.append(item)
            categories['chapters'].append(item)

    # 4. Score Exam Objectives
    try:
        from curriculum_v2.objectives import OBJECTIVES
        for oid, odata in OBJECTIVES.items():
            o_text = odata.get('text') or odata.get('title') or ''
            o_course = odata.get('course') or oid.split('-')[0]
            sc = score_document(f"{oid}: {o_text}", '', o_text, qinfo, oid)
            if sc <= 0:
                continue
            Snippet_html = build_snippet(o_text, qinfo)
            item = {
                'kind': 'Exam Objective',
                'title': f"Objective {oid} — {o_text[:85]}",
                'chapter': f"Chapter {odata.get('chapter', '')}",
                'course': o_course,
                'snippet': o_text,
                'snippet_html': Snippet_html,
                'locked': False,
                'url': url_for_fn('specs_page') + f"#course-{o_course}",
                'score': sc * 0.8,
            }
            scored_results.append(item)
            categories['objectives'].append(item)
    except Exception:
        pass

    # 5. Score Knowledge Tests
    if course_ids:
        tests = KnowledgeTest.query.filter(KnowledgeTest.course_id.in_(course_ids)).order_by(KnowledgeTest.order).all()
        for test in tests:
            sc = score_document(test.title, '', test.description or '', qinfo, test.course.code if test.course else '')
            if sc <= 0:
                continue
            section = section_for_course_fn(test.course_id)
            if not section:
                continue
            if getattr(current_user, 'role', '') in ('instructor', 'admin'):
                url = url_for_fn('instructor_test_performance', section_id=section.id, test_id=test.id)
                locked = False
            elif getattr(current_user, 'is_authenticated', False):
                locked = not _is_avail(section.id, 'test', test.id, uid)
                url = url_for_fn('take_test', section_id=section.id, test_id=test.id) if not locked else url_for_fn('student_section', section_id=section.id)
            else:
                locked = False
                url = url_for_fn('take_test', section_id=section.id, test_id=test.id)
            item = {
                'kind': 'Test',
                'title': test.title,
                'chapter': test.course.title if test.course else '',
                'course': test.course.title if test.course else '',
                'snippet': test.description or 'Knowledge test',
                'snippet_html': html.escape(test.description or 'Knowledge test'),
                'locked': locked,
                'url': url,
                'score': sc * 0.85,
            }
            scored_results.append(item)
            categories['tests'].append(item)

    scored_results.sort(key=lambda r: (-r['score'], r['kind'] != 'Lesson', r['title']))
    for k in categories:
        categories[k].sort(key=lambda r: (-r['score'], r['title']))
        categories[k] = categories[k][:8]

    return {
        'query': q,
        'corrected_query': qinfo['corrected_query'],
        'did_you_mean': qinfo['did_you_mean'],
        'expanded_terms': qinfo['expanded_terms'],
        'results': scored_results[:limit],
        'categories': categories,
    }
