"""New labs added on the ``labs`` branch (pass L1).

Each lab uses the standard lab format (``interactive_labs._lab``) plus:
  course_objectives  objective codes the lab assesses (curriculum_v2/objectives.py)
  steps              graded steps (activity labs) or checkpoint questions (terminal / GUI labs)
  auto               state-based grader for terminal labs: auto(state, done, cmd, lines) -> extra lines
  gui_rules          objective rules for Windows 11 GUI labs (see labs_gui)
  obj_hints          {objective: [nudge, exact action]} — tiered hints
  solution           a known-good path (used by verify_all_labs and the e2e tests)
  minutes            estimated time
"""
import ipaddress
import re

from labs_activity import mask_from_any, norm
from labs_gui import default_ad, gui_state
from labs_linux import HOME, linux_state


def _lab(id, title, kind, blurb, objectives, intro, success_msg, initial_state, **extra):
    lab = {"id": id, "title": title, "kind": kind, "blurb": blurb, "objectives": objectives, "intro": intro,
           "success_msg": success_msg, "initial_state": initial_state, "hints": extra.pop("hints", []),
           "builds_on": extra.pop("builds_on", [])}
    lab.update(extra)
    return lab


def _choice(id, objective, prompt, options, answer, explain=None, right=None, multi=False, title=None):
    st = {"id": id, "type": "choice", "objective": objective, "prompt": prompt, "options": options, "answer": answer,
          "explain": {str(k): v for k, v in (explain or {}).items()}, "multi": multi}
    if right:
        st["right"] = right
    if title:
        st["title"] = title
    return st


# ────────────────────────────────────────────────────────────── net-subnet

def _net(vals):
    return ipaddress.ip_network(f"{vals['ip']}/{vals['prefix']}", strict=False)


def _ipeq(want):
    def chk(got, vals, ans):
        try:
            return ipaddress.ip_address(str(got).strip()) == want(vals), ''
        except ValueError:
            return False, 'enter a dotted-decimal address such as 192.168.1.0.'
    return chk


def _chk_network(got, vals, ans):
    n = _net(vals)
    ok, why = _ipeq(lambda v: n.network_address)(got, vals, ans)
    if not ok and not why:
        why = f'block size is {n.num_addresses}; the network address is the multiple of {n.num_addresses} at or below the host.'
    return ok, why


def _chk_broadcast(got, vals, ans):
    n = _net(vals)
    ok, why = _ipeq(lambda v: n.broadcast_address)(got, vals, ans)
    return ok, why or 'broadcast = next network address minus 1.'


def _chk_first(got, vals, ans):
    n = _net(vals)
    return _ipeq(lambda v: n.network_address + 1)(got, vals, ans)[0], 'first usable = network address + 1.'


def _chk_last(got, vals, ans):
    n = _net(vals)
    return _ipeq(lambda v: n.broadcast_address - 1)(got, vals, ans)[0], 'last usable = broadcast address - 1.'


def _chk_usable(got, vals, ans):
    want = 2 ** (32 - vals['prefix']) - 2
    try:
        return int(str(got).strip()) == want, 'usable hosts = 2^(host bits) - 2.'
    except ValueError:
        return False, 'enter a number.'


def _chk_mask(got, vals, ans):
    p = mask_from_any(got)
    return p == vals['prefix'], f'/{vals["prefix"]} has {vals["prefix"]} one-bits; write it as four octets.'


def _need_prefix(need):
    for p in range(30, 0, -1):
        if 2 ** (32 - p) - 2 >= need:
            return p
    return 1


def _chk_need_prefix(got, vals, ans):
    p = mask_from_any(got)
    want = _need_prefix(vals['need'])
    if p is None:
        return False, 'enter /n or a dotted mask.'
    if p > want:
        return False, f'/{p} gives only {2 ** (32 - p) - 2} usable hosts — too small.'
    if p < want:
        return False, f'/{p} fits but wastes addresses; the smallest subnet that fits is larger than that prefix.'
    return True, ''


def _chk_need_usable(got, vals, ans):
    want = 2 ** (32 - _need_prefix(vals['need'])) - 2
    try:
        return int(str(got).strip()) == want, 'usable hosts in the subnet you chose.'
    except ValueError:
        return False, 'enter a number.'


def subnet_solution(state):
    v = state['gen']['s1']
    n = _net(v)
    need = state['gen']['s2']['need']
    p = _need_prefix(need)
    return {
        's1': {'network': str(n.network_address), 'broadcast': str(n.broadcast_address), 'first': str(n.network_address + 1),
               'last': str(n.broadcast_address - 1), 'usable': str(n.num_addresses - 2), 'mask': str(n.netmask)},
        's2': {'prefix': f'/{p}', 'usable': str(2 ** (32 - p) - 2)},
        's3': 2, 's4': 1,
    }


NET_SUBNET = _lab(
    "net-subnet", "Subnetting Workbench", "activity",
    "Per-student subnet values: network, broadcast, host range, mask; size a subnet; spot invalid hosts and APIPA.",
    [
        {"id": "subnet_math", "text": "Work out network, broadcast, host range, usable hosts and mask for your address"},
        {"id": "size_subnet", "text": "Choose the smallest subnet that fits a department"},
        {"id": "host_valid", "text": "Spot the address that cannot be assigned to a host"},
        {"id": "apipa", "text": "Interpret a 169.254.x.x address"},
    ],
    "Every student gets different numbers, so work it out — a calculator for the binary is fine, a subnet calculator website is not.",
    "Subnet math done. You can size and validate a subnet the way the network team expects.",
    {"kind": "activity"},
    course_objectives=["NO-1.2", "IT-5.1"], minutes=25,
    steps=[
        {"id": "s1", "type": "fields", "objective": "subnet_math", "gen": "subnet", "title": "Your host address",
         "prompt": "A PC is configured as {ip}/{prefix}. Fill in its subnet.",
         "help": "Block size = 2^(32 - prefix). Find the multiple of the block size at or below the host's last changing octet.",
         "fields": [
             {"name": "network", "label": "Network address", "placeholder": "e.g. 192.168.1.0", "inputmode": "decimal", "check": _chk_network},
             {"name": "broadcast", "label": "Broadcast address", "inputmode": "decimal", "check": _chk_broadcast},
             {"name": "first", "label": "First usable host", "inputmode": "decimal", "check": _chk_first},
             {"name": "last", "label": "Last usable host", "inputmode": "decimal", "check": _chk_last},
             {"name": "usable", "label": "Usable hosts", "inputmode": "numeric", "check": _chk_usable},
             {"name": "mask", "label": "Subnet mask (dotted)", "placeholder": "255.255.255.x", "inputmode": "decimal", "check": _chk_mask},
         ]},
        {"id": "s2", "type": "fields", "objective": "size_subnet", "gen": "hosts_needed", "title": "Size a subnet",
         "prompt": "The Facilities team needs {need} addresses for hosts on one VLAN (gateway included). Pick the smallest subnet that fits.",
         "help": "Usable hosts = 2^(host bits) - 2. Grow the host bits until it fits.",
         "fields": [
             {"name": "prefix", "label": "Prefix (/n or dotted mask)", "placeholder": "/26", "check": _chk_need_prefix},
             {"name": "usable", "label": "Usable hosts in that subnet", "inputmode": "numeric", "check": _chk_need_usable},
         ]},
        _choice("s3", "host_valid", "Which address can NOT be assigned to a host on 192.168.10.0/23?",
                ["192.168.10.255", "192.168.11.0", "192.168.11.255", "192.168.10.1"], 2,
                {0: "A /23 spans 192.168.10.0–192.168.11.255, so .10.255 is in the middle of the range — a valid host.",
                 1: "192.168.11.0 is in the middle of the /23 range — valid. Only the first and last addresses are reserved.",
                 3: "192.168.10.1 is the first usable host (often the gateway)."},
                right="Correct: 192.168.11.255 is the broadcast address of 192.168.10.0/23."),
        _choice("s4", "apipa", "A laptop shows IPv4 169.254.37.12, mask 255.255.0.0, no gateway. What does it tell you?",
                ["The DNS server is down", "The client asked for DHCP and got no answer (APIPA self-assigned)",
                 "The IP address conflicts with another device", "The laptop is on the guest VLAN"], 1,
                {0: "DNS failure doesn't change the IP address. Look at the address range.",
                 2: "A conflict shows a duplicate-address warning; 169.254/16 is self-assigned.",
                 3: "A guest VLAN still hands out a normal DHCP address."},
                right="Correct: 169.254.0.0/16 is APIPA — check link, VLAN and the DHCP server/relay next."),
    ],
    obj_hints={
        "subnet_math": ["Block size first: 2^(32 - prefix).", "Network = host address rounded down to a multiple of the block size; broadcast = network + block - 1."],
        "size_subnet": ["Count host bits: 2^h - 2 must be ≥ the hosts needed.", "Find the smallest h that fits, then prefix = 32 - h."],
        "host_valid": ["Write out where a /23 starts and ends.", "Only the very first (network) and very last (broadcast) addresses of the /23 are reserved."],
        "apipa": ["What range is 169.254.0.0/16?", "It is APIPA: the DHCP request got no reply."],
    },
    solution={"answers": subnet_solution},
)

# ────────────────────────────────────────────────────────────── hw-cables

def _svg(body, label):
    return (f'<svg viewBox="0 0 96 64" role="img" aria-label="{label}" class="lab-conn" xmlns="http://www.w3.org/2000/svg">'
            f'<g fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round">{body}</g></svg>')


CONNECTORS = [
    ("rj45", "RJ45", _svg('<rect x="28" y="10" width="40" height="40" rx="3"/><path d="M36 50v8h24v-8"/>'
                          '<path d="M34 16v12M40 16v12M46 16v12M52 16v12M58 16v12M62 16v12" stroke-width="1.6"/>', "Square clear plug with eight gold pins and a latch"),
     "Wide square plug, 8 pins, latch on the back"),
    ("rj11", "RJ11", _svg('<rect x="34" y="14" width="28" height="34" rx="3"/><path d="M40 48v8h16v-8"/>'
                          '<path d="M42 20v10M48 20v10M54 20v10" stroke-width="1.6"/>', "Narrow clear plug with 4-6 pins"),
     "Narrow plug, 4–6 pins, latch — smaller than a network plug"),
    ("usbc", "USB-C", _svg('<rect x="22" y="24" width="52" height="16" rx="8"/><rect x="32" y="30" width="32" height="4" rx="2"/>',
                           "Small rounded oval plug, reversible"),
     "Small oval, reversible (no up or down)"),
    ("usba", "USB-A", _svg('<rect x="24" y="20" width="48" height="24" rx="1"/><rect x="30" y="26" width="36" height="7"/>',
                           "Flat rectangle with a plastic tongue on one side"),
     "Flat rectangle, plastic tongue, only fits one way"),
    ("hdmi", "HDMI", _svg('<path d="M18 22h60v12l-8 8H26l-8-8z"/>', "Wide plug with tapered lower corners, symmetrical"),
     "Wide plug, both lower corners tapered (19 pins)"),
    ("dp", "DisplayPort", _svg('<path d="M18 22h60v20H28l-10-8z"/>', "Wide plug with only one corner cut, and a release button"),
     "Wide plug, only ONE corner cut, release button on top"),
    ("lc", "LC fiber", _svg('<rect x="26" y="18" width="16" height="30" rx="2"/><rect x="54" y="18" width="16" height="30" rx="2"/>'
                            '<path d="M34 10v8M62 10v8M30 48h8M58 48h8"/>', "Two small square push-latch ferrules side by side"),
     "Pair of small square connectors with ceramic ferrules (duplex)"),
    ("ftype", "F-type coax", _svg('<path d="M30 16l6-6h24l6 6v32l-6 6H36l-6-6z"/><circle cx="48" cy="32" r="3"/>',
                                  "Hexagonal screw-on connector with a single centre wire"),
     "Hex screw-on nut, single copper centre wire"),
]

CABLE_JOBS = [
    ("job_10g", "10 Gb/s copper to a desk 80 m from the switch", "cat6a", "Cat 6 only reaches 10 Gb/s to about 55 m; Cat 6A does 100 m."),
    ("job_bldg", "Link between two buildings 2 km apart", "smf", "Copper stops at 100 m; multimode is for shorter runs. 2 km = single-mode fiber."),
    ("job_isp", "Cable modem to the ISP wall outlet", "rg6", "Cable internet arrives on coax (RG-6 with F-type connectors)."),
    ("job_dock", "Laptop to dock: video, data and charging on one cable", "usbc", "USB-C / Thunderbolt carries DisplayPort alt mode, data and power delivery."),
    ("job_dsl", "Analog phone line to a DSL filter", "rj11", "Phone/DSL uses the small RJ11 plug."),
    ("job_tv", "Training-room TV that only has HDMI inputs", "hdmi", "Match the display's input: HDMI."),
]

HW_CABLES = _lab(
    "hw-cables", "Cable & Connector Identification", "activity",
    "Identify eight connectors by shape, pick the right cable for six jobs, and choose the right test tool.",
    [
        {"id": "id_connectors", "text": "Match each connector drawing to its name"},
        {"id": "pick_cable", "text": "Pick the right cable for each job"},
        {"id": "tool", "text": "Choose the right tool to verify a new keystone jack"},
    ],
    "Bench drawer of unlabelled cables. Drag (or tap, then tap the target) to match. On a phone, tap an item then tap where it goes.",
    "Connectors and cables identified. You can now pick media for a job and test it.",
    {"kind": "activity"},
    course_objectives=["IT-3.4", "NO-2.3"], minutes=15,
    steps=[
        {"id": "c1", "type": "match", "objective": "id_connectors", "title": "Name the connectors",
         "prompt": "Match each drawing to the connector name.",
         "items": [{"id": cid, "label": desc, "svg": svg, "answer": "t_" + cid} for cid, name, svg, desc in CONNECTORS],
         "targets": [{"id": "t_" + cid, "label": name} for cid, name, svg, desc in CONNECTORS],
         "right": "All eight identified."},
        {"id": "c2", "type": "match", "objective": "pick_cable", "title": "Pick the cable for the job",
         "prompt": "Match each job to the cable you would take from the drawer.",
         "items": [{"id": jid, "label": text, "answer": ans, "tip": tip} for jid, text, ans, tip in CABLE_JOBS],
         "targets": [{"id": "cat6a", "label": "Cat 6A patch/horizontal"}, {"id": "smf", "label": "Single-mode fiber (LC)"},
                     {"id": "rg6", "label": "RG-6 coax (F-type)"}, {"id": "usbc", "label": "USB-C / Thunderbolt"},
                     {"id": "rj11", "label": "RJ11 phone cord"}, {"id": "hdmi", "label": "HDMI"}],
         "right": "Right media for every job."},
        _choice("c3", "tool", "You just punched down a new keystone jack. Which tool proves all eight wires are in the right order?",
                ["Toner and probe", "Cable tester (wire-map)", "Loopback plug", "Multimeter on AC volts"], 1,
                {0: "A toner finds which cable is which in a bundle; it doesn't check the pin order.",
                 2: "A loopback plug tests a port's transmit/receive, not the cable's wire map.",
                 3: "Never put AC-volts probes on network cabling; it doesn't show the wire map."},
                right="Correct: a cable tester's wire map shows opens, shorts, split and crossed pairs."),
    ],
    obj_hints={
        "id_connectors": ["Look at the corners: HDMI tapers both, DisplayPort only one.", "RJ45 is wider with 8 pins; RJ11 has 4–6. F-type has a hex nut."],
        "pick_cable": ["Distance decides first: copper ≤ 100 m.", "Over 100 m between buildings use fiber; the ISP cable modem uses coax."],
        "tool": ["Which tool shows each pin's mapping?", "The cable tester (wire-map)."],
    },
    solution={"answers": {"c1": {cid: "t_" + cid for cid, *_ in CONNECTORS}, "c2": {j: a for j, _, a, _ in CABLE_JOBS}, "c3": 1}},
)

# ────────────────────────────────────────────────────────────── hw-pc-build

_CPUS = [
    {"id": "i5", "label": "Intel Core i5-14500", "specs": "LGA1700 · 14 cores · 65 W (154 W turbo) · integrated graphics", "price": 230,
     "socket": "LGA1700", "watts": 154, "igpu": True},
    {"id": "r7", "label": "AMD Ryzen 7 7700", "specs": "AM5 · 8 cores · 65 W (88 W PPT) · integrated graphics", "price": 290,
     "socket": "AM5", "watts": 88, "igpu": True},
    {"id": "i7k", "label": "Intel Core i7-14700K", "specs": "LGA1700 · 20 cores · 125 W (253 W turbo) · integrated graphics", "price": 390,
     "socket": "LGA1700", "watts": 253, "igpu": True},
    {"id": "r5", "label": "AMD Ryzen 5 5600", "specs": "AM4 · 6 cores · 65 W · no integrated graphics", "price": 120,
     "socket": "AM4", "watts": 76, "igpu": False},
]
_BOARDS = [
    {"id": "b760m", "label": "B760M micro-ATX", "specs": "LGA1700 · DDR5 · micro-ATX · 2× M.2 NVMe · DP + HDMI · fTPM (PTT)", "price": 150,
     "socket": "LGA1700", "ram": "DDR5", "ff": "mATX", "m2": True},
    {"id": "b760d4", "label": "B760 ATX (DDR4)", "specs": "LGA1700 · DDR4 · ATX · 1× M.2 NVMe · HDMI · fTPM (PTT)", "price": 140,
     "socket": "LGA1700", "ram": "DDR4", "ff": "ATX", "m2": True},
    {"id": "b650m", "label": "B650M micro-ATX", "specs": "AM5 · DDR5 · micro-ATX · 2× M.2 NVMe · DP + HDMI · fTPM", "price": 160,
     "socket": "AM5", "ram": "DDR5", "ff": "mATX", "m2": True},
    {"id": "b550", "label": "B550 ATX", "specs": "AM4 · DDR4 · ATX · 1× M.2 NVMe · HDMI · fTPM", "price": 110,
     "socket": "AM4", "ram": "DDR4", "ff": "ATX", "m2": True},
]
_RAM = [
    {"id": "d5_32", "label": "32 GB DDR5-5600 (2×16)", "specs": "DDR5 · dual channel", "price": 95, "type": "DDR5", "gb": 32},
    {"id": "d4_32", "label": "32 GB DDR4-3200 (2×16)", "specs": "DDR4 · dual channel", "price": 70, "type": "DDR4", "gb": 32},
    {"id": "d5_16", "label": "16 GB DDR5-5600 (1×16)", "specs": "DDR5 · single stick", "price": 50, "type": "DDR5", "gb": 16},
]
_DISKS = [
    {"id": "nvme", "label": "1 TB NVMe PCIe 4.0 M.2", "specs": "M.2 2280 · ~7000 MB/s", "price": 80, "nvme": True},
    {"id": "hdd", "label": "2 TB 7200 rpm SATA HDD", "specs": "3.5\" SATA · ~200 MB/s", "price": 55, "nvme": False},
    {"id": "ssd25", "label": "1 TB 2.5\" SATA SSD", "specs": "SATA III · ~550 MB/s", "price": 70, "nvme": False},
]
_GPUS = [
    {"id": "none", "label": "None — use integrated graphics", "specs": "Outputs from the motherboard only", "price": 0, "watts": 0, "dp": 0, "len": 0},
    {"id": "rtx4060", "label": "GeForce RTX 4060 8 GB", "specs": "3× DisplayPort + 1× HDMI · 115 W · one 8-pin · 240 mm", "price": 300,
     "watts": 115, "dp": 3, "len": 240},
    {"id": "gt710", "label": "GeForce GT 710 2 GB", "specs": "VGA + DVI + HDMI · 19 W · 170 mm", "price": 50, "watts": 19, "dp": 0, "len": 170},
]
_PSUS = [
    {"id": "p300", "label": "300 W generic", "specs": "No efficiency rating · no PCIe 8-pin", "price": 25, "w": 300, "pcie": False},
    {"id": "p450", "label": "450 W 80 PLUS Bronze", "specs": "1× PCIe 8-pin", "price": 55, "w": 450, "pcie": True},
    {"id": "p650", "label": "650 W 80 PLUS Gold", "specs": "2× PCIe 8-pin · modular", "price": 95, "w": 650, "pcie": True},
]
_CASES = [
    {"id": "itx", "label": "Mini-ITX compact", "specs": "Fits Mini-ITX boards only · GPU ≤ 200 mm", "price": 70, "fits": ["ITX"], "gpu": 200},
    {"id": "matx", "label": "Micro-ATX tower", "specs": "Fits micro-ATX and Mini-ITX · GPU ≤ 330 mm", "price": 80, "fits": ["mATX", "ITX"], "gpu": 330},
    {"id": "atx", "label": "ATX mid tower", "specs": "Fits ATX, micro-ATX, Mini-ITX · GPU ≤ 360 mm", "price": 95, "fits": ["ATX", "mATX", "ITX"], "gpu": 360},
]


def _validate_build(p):
    cpu, mb, ram, disk, gpu, psu, case = (p[k] for k in ("cpu", "board", "ram", "storage", "gpu", "psu", "case"))
    issues = []
    if cpu["socket"] != mb["socket"]:
        issues.append(("board", f"{cpu['label']} is {cpu['socket']}; the {mb['label']} is {mb['socket']} — the CPU will not fit."))
    if ram["type"] != mb["ram"]:
        issues.append(("ram", f"The board takes {mb['ram']}; {ram['type']} is keyed differently and will not seat."))
    if ram["gb"] < 32:
        issues.append(("ram", "The ticket asks for 32 GB."))
    if not disk["nvme"]:
        issues.append(("storage", "The requirement is an NVMe boot drive."))
    if mb["ff"] not in case["fits"]:
        issues.append(("case", f"A {mb['ff']} board does not fit the {case['label']}."))
    if gpu["len"] > case["gpu"]:
        issues.append(("case", f"The {gpu['label']} is {gpu['len']} mm; the case takes {case['gpu']} mm."))
    dp = gpu["dp"] if gpu["id"] != "none" else (1 if cpu["igpu"] and "DP" in mb["specs"] else 0)
    if not cpu["igpu"] and gpu["id"] == "none":
        issues.append(("gpu", f"The {cpu['label']} has no integrated graphics — with no card there is no video at all."))
    elif dp < 2:
        issues.append(("gpu", "Two DisplayPort monitors need two DisplayPort outputs; this build has " + str(dp) + "."))
    need = round((cpu["watts"] + gpu["watts"] + 75) * 1.3)
    if psu["w"] < need:
        issues.append(("psu", f"Estimated load {cpu['watts'] + gpu['watts'] + 75} W; with 30 % headroom you need about {need} W."))
    if gpu["watts"] > 75 and not psu["pcie"]:
        issues.append(("psu", "The graphics card needs a PCIe 8-pin power lead this PSU does not have."))
    return issues


HW_PC_BUILD = _lab(
    "hw-pc-build", "Workstation Component Selection", "activity",
    "Spec a CAD workstation from a parts list: socket, memory type, form factor, power budget, outputs and price.",
    [
        {"id": "build_ok", "text": "Pick a compatible build that meets every requirement and the budget"},
        {"id": "uefi", "text": "Choose the firmware settings Windows 11 needs"},
    ],
    "Ticket REQ-2210: CAD workstation for the drafting office. Requirements: 32 GB RAM, NVMe boot drive, two DisplayPort monitors, "
    "Windows 11, budget $1,400 for the parts listed. The checker tells you what clashes — like a real compatibility check.",
    "Build approved: compatible, powered with headroom, within budget, ready for Windows 11.",
    {"kind": "activity"},
    course_objectives=["IT-2.1", "IT-2.2", "IT-3.1", "IT-3.3"], minutes=20,
    steps=[
        {"id": "b1", "type": "build", "objective": "build_ok", "title": "Pick the parts", "budget": 1400,
         "prompt": "One part per slot. Check the build; fix whatever the checker flags.",
         "slots": [{"name": "cpu", "label": "Processor", "options": _CPUS}, {"name": "board", "label": "Motherboard", "options": _BOARDS},
                   {"name": "ram", "label": "Memory", "options": _RAM}, {"name": "storage", "label": "Boot drive", "options": _DISKS},
                   {"name": "gpu", "label": "Graphics", "options": _GPUS}, {"name": "psu", "label": "Power supply", "options": _PSUS},
                   {"name": "case", "label": "Case", "options": _CASES}],
         "validate": _validate_build},
        _choice("b2", "uefi", "Before installing Windows 11 on the new build, which firmware settings must be on?",
                ["Legacy/CSM boot and XMP off", "UEFI boot with Secure Boot, and the firmware TPM (Intel PTT / AMD fTPM) enabled",
                 "Fast Boot and virtualization (VT-x) only", "RAID mode for the NVMe drive"], 1,
                {0: "Windows 11 needs UEFI; Legacy/CSM breaks Secure Boot.",
                 2: "Those are optional. The Windows 11 checks are UEFI + Secure Boot capable + TPM 2.0.",
                 3: "RAID mode can hide the NVMe drive from Setup without a driver; AHCI/NVMe default is right."},
                right="Correct: UEFI + Secure Boot + TPM 2.0 (PTT/fTPM)."),
    ],
    obj_hints={
        "build_ok": ["Start with the CPU socket and match the board; then the board decides the RAM type and case size.",
                     "One valid build: i5-14500 + B760M + 32 GB DDR5 + NVMe + RTX 4060 + 450 W Bronze + micro-ATX tower."],
        "uefi": ["What does the Windows 11 PC Health Check look for?", "UEFI with Secure Boot, and TPM 2.0 (PTT/fTPM)."],
    },
    solution={"answers": {"b1": {"cpu": "i5", "board": "b760m", "ram": "d5_32", "storage": "nvme", "gpu": "rtx4060",
                                 "psu": "p450", "case": "matx"}, "b2": 1}},
)

# ────────────────────────────────────────────────────────────── ticket-method

METHOD = ["Identify the problem", "Establish a theory of probable cause", "Test the theory to determine the cause",
          "Establish a plan of action and implement the solution", "Verify full system functionality and implement preventive measures",
          "Document findings, actions and outcomes"]


def _chk_note(got, vals, ans):
    t = norm(got)
    if len(t) < 60:
        return False, 'write at least two sentences: cause, action, verification.'
    if any(w in t for w in ("password is", "password:", "pw:", "new password")) and any(c.isdigit() for c in t):
        return False, 'never write a password in a ticket note.'
    miss = []
    if not any(w in t for w in ("password", "credential", "cached")):
        miss.append('the cause (stale cached password)')
    if not any(w in t for w in ("re-enter", "reentered", "re-entered", "updated", "cleared", "removed", "entered", "signed in")):
        miss.append('what you did')
    if not any(w in t for w in ("test", "sent", "confirmed", "verified", "receiv")):
        miss.append('how you verified it')
    if miss:
        return False, 'add ' + ', '.join(miss) + '.'
    return True, ''


TICKET_METHOD = _lab(
    "ticket-method", "Troubleshooting Methodology", "activity",
    "Order the six-step method, then use it on a live ticket: question, theory, least-disruptive test, verify, document.",
    [
        {"id": "order_steps", "text": "Put the troubleshooting steps in order"},
        {"id": "identify", "text": "Ask the identifying question first"},
        {"id": "theory", "text": "Pick the most probable cause from the evidence"},
        {"id": "test", "text": "Choose the least disruptive test of the theory"},
        {"id": "verify", "text": "Verify full functionality with the user"},
        {"id": "document", "text": "Write the closing note (cause → action → verification)"},
    ],
    "INC-30417 from Dana (Accounts): \"Outlook won't send anything since this morning. It just sits in the Outbox.\"",
    "Ticket worked in order and documented so another technician could verify it.",
    {"kind": "activity"},
    course_objectives=["IT-7.1", "IT-7.2", "IT-7.3", "IT-1.3", "NO-6.1"], minutes=20,
    steps=[
        {"id": "m1", "type": "order", "objective": "order_steps", "title": "The method", "items": METHOD,
         "prompt": "Put the six steps in order (drag, or use the move buttons).",
         "tips": {METHOD[0]: "You cannot form a theory before you know the symptom and scope.",
                  METHOD[2]: "A theory is tested before you plan a fix.",
                  METHOD[4]: "Verify before you document and close.",
                  METHOD[5]: "Documentation is the last step."}},
        _choice("m2", "identify", "Step 1 with Dana. Which question do you ask first?",
                ["Can I reinstall Office for you?", "When did it last work, what changed since, and is anyone else affected?",
                 "Have you restarted?", "Which version of Windows do you have?"], 1,
                {0: "That's a fix, not a question — and a disruptive one.", 2: "Fine later, but it doesn't identify the problem or its scope.",
                 3: "You can find that yourself; it doesn't scope the fault."},
                right="Right: time, change and scope first."),
        _choice("m3", "theory", "Evidence: colleagues on the same floor can send; Dana can send from webmail; Outlook's status bar says "
                "\"Need password\"; Dana changed her password on her phone last night. Most probable cause?",
                ["The mail server is down", "Outlook is still using the old cached password", "The network switch on her floor failed",
                 "Her mailbox is full"], 1,
                {0: "Colleagues and webmail work — the server is fine.", 2: "Others on the floor can send, and webmail works from her PC.",
                 3: "A full mailbox blocks sending in webmail too, with a quota message."},
                right="Right: the password change plus \"Need password\" points at stale cached credentials."),
        _choice("m4", "test", "Which is the least disruptive test of that theory?",
                ["Rebuild her Outlook profile", "Re-image the PC", "Click \"Need password\" (or check Credential Manager) and sign in with the new password",
                 "Reset her password again"], 2,
                {0: "That might work but loses local settings — try the small test first.", 1: "Far too disruptive for a credential symptom.",
                 3: "Another reset makes things worse; she already has a working password."},
                right="Right: smallest change that proves or disproves the theory."),
        _choice("m5", "verify", "The Outbox empties. Which actions verify full functionality? (choose all that apply)",
                ["Have Dana send a test to an internal and an external address", "Confirm the replies arrive", "Check the Sent Items folder",
                 "Close the ticket straight away — it's fixed"], [0, 1, 2],
                {3: "Closing without the user confirming skips the verification step."}, multi=True,
                right="Right: verify send and receive, with the user."),
        {"id": "m6", "type": "fields", "objective": "document", "title": "Closing note",
         "prompt": "Write the closing note: cause → action → verification. No passwords in tickets.",
         "fields": [{"name": "note", "label": "Ticket note", "multiline": True,
                     "placeholder": "Cause: … Action: … Verified: …", "check": _chk_note}]},
    ],
    obj_hints={
        "order_steps": ["Identify comes first, Document last.", "Identify → Theory → Test → Plan/Implement → Verify → Document."],
        "identify": ["Scope and change.", "When did it last work, what changed, who else is affected?"],
        "theory": ["What changed last night?", "Stale cached password."],
        "test": ["Smallest change first.", "Re-enter the new password when Outlook prompts."],
        "verify": ["Verify send AND receive with the user.", "Internal + external test, replies arrive, Sent Items."],
        "document": ["Three parts: cause, action, verification.",
                     "e.g. Cause: Outlook cached the old password after Dana's reset. Action: re-entered credentials at the prompt. Verified: test mail sent and received."],
    },
    solution={"answers": {"m1": METHOD, "m2": 1, "m3": 1, "m4": 2, "m5": [0, 1, 2],
                          "m6": {"note": "Cause: Outlook cached the old password after Dana changed it on her phone. Action: re-entered "
                                         "her credentials at the Need password prompt. Verified: test mail sent internally and externally and replies received."}}},
)

# ────────────────────────────────────────────────────────────── win-net-cli (Windows CLI, DNS primary down)


def _win(**extra):
    """Windows VM state; interactive_labs fills in the standard base (_win_state) when it installs these labs."""
    return {"_base": "win", **extra}


WIN_NET_CLI = _lab(
    "win-net-cli", "Windows CLI — DNS Fault Isolation", "windows",
    "Link, IP, gateway, internet by IP, path, then names: prove the primary DNS server is the fault with evidence.",
    [
        {"id": "run_ipconfig", "text": "ipconfig /all — note BOTH DNS servers"},
        {"id": "ping_gw", "text": "Ping the default gateway"},
        {"id": "ping_ext", "text": "Ping 1.1.1.1 (internet by IP)"},
        {"id": "tracert_ext", "text": "tracert 1.1.1.1 and read the path"},
        {"id": "ping_name_fail", "text": "Ping intranet.training.local by name — and see it fail"},
        {"id": "ns_primary_fail", "text": "nslookup intranet.training.local (uses the primary DNS)"},
        {"id": "ns_secondary_ok", "text": "nslookup intranet.training.local 10.20.30.11 (ask the secondary)"},
        {"id": "netstat", "text": "netstat -an — confirm DNS queries leave for 10.20.30.10:53"},
        {"id": "q_fault", "text": "Checkpoint: name the faulty component"},
        {"id": "q_next", "text": "Checkpoint: choose the next action"},
    ],
    "INC-30502: \"The intranet won't load but Google does.\" Work bottom-up: IP and gateway, internet by IP, then names. "
    "Change nothing yet — collect evidence.",
    "Fault isolated with evidence: the primary DNS server is not answering; the secondary resolves.",
    _win(dns_primary_down=True, ext_hosts={"1.1.1.1": 12, "8.8.8.8": 14},
                   name_map={"gateway.training.local": "10.20.30.1", "intranet.training.local": "10.20.30.80",
                             "files.training.local": "10.20.30.50"},
                   pingable_ips=["127.0.0.1", "10.20.30.1", "10.20.30.47", "10.20.30.50", "10.20.30.11", "10.20.30.80"]),
    course_objectives=["IT-5.3", "IT-13.1", "IT-13.2", "NO-4.2"], minutes=20,
    hints=["ipconfig /all", "ping 10.20.30.1", "ping 1.1.1.1", "tracert 1.1.1.1", "ping intranet.training.local",
           "nslookup intranet.training.local", "nslookup intranet.training.local 10.20.30.11", "netstat -an"],
    palette=["ipconfig /all", "ping ", "tracert ", "nslookup ", "netstat -an", "ipconfig /flushdns", "cls", "help"],
    steps=[
        _choice("q_fault", "q_fault", "From your evidence, which component is at fault?",
                ["The default gateway 10.20.30.1", "The primary DNS server 10.20.30.10", "The PC's network adapter driver",
                 "The intranet web server 10.20.30.80"], 1,
                {0: "The gateway answered and 1.1.1.1 is reachable through it.",
                 2: "The adapter carries traffic fine — internet by IP works.",
                 3: "The name never resolves via the primary, so you haven't reached the web server yet; the secondary resolves it."},
                right="Correct: the primary DNS server times out; the secondary answers.", title="Checkpoint"),
        _choice("q_next", "q_next", "What is the right next action for the help desk?",
                ["Hard-code 8.8.8.8 as DNS on the user's PC and close the ticket",
                 "Escalate to the server team with the nslookup/ping evidence; tell the user the workaround and the next update time",
                 "Reinstall the network driver", "Run netsh winsock reset and reboot"], 1,
                {0: "A public resolver can't resolve internal names like intranet.training.local, and it hides the outage from others.",
                 2: "The adapter is fine.", 3: "A disruptive reset that cannot fix a server-side fault."},
                right="Correct: the fix is server-side; escalate with evidence and keep the user informed.", title="Checkpoint"),
    ],
    solution={"commands": ["ipconfig /all", "ping 10.20.30.1", "ping 1.1.1.1", "tracert 1.1.1.1", "ping intranet.training.local",
                           "nslookup intranet.training.local", "nslookup intranet.training.local 10.20.30.11", "netstat -an"],
              "answers": {"q_fault": 1, "q_next": 1}},
)

# ────────────────────────────────────────────────────────────── linux-shell

SUP = HOME + "/support"


def _linux_rules(state, done, ev):
    f = state.setdefault("facts", [])
    kind = ev[0]
    fs = state["fs"]

    def m(oid):
        if oid not in done:
            done.append(oid)
    if kind in ("whoami", "hostname"):
        if kind not in f:
            f.append(kind)
        if "whoami" in f and "hostname" in f:
            m("identify")
    elif kind == "ls-l" and ev[1] == SUP:
        m("navigate")
        if "report.txt" in ev[2] and not (fs[SUP + "/report.txt"]["mode"] & 0o004) and "private" in f:
            m("private")
    elif kind == "ls-l" and ev[1] == SUP + "/report.txt" and "private" in f and not (fs[ev[1]]["mode"] & 0o004):
        m("private")
    elif kind == "mkdir" and ev[1] == SUP + "/logs":
        m("mkdir")
    elif kind == "write" and ev[1] == SUP + "/logs/notes.txt" and ev[2].strip():
        m("notes")
    elif kind == "chmod" and ev[1] == SUP + "/report.txt":
        mode = ev[2]
        if not (mode & 0o004) and (mode & 0o400):
            if "private" not in f:
                f.append("private")
            return ["(report.txt is no longer readable by others. Verify it: ls -l)"]
    elif kind == "exec" and ev[1] == SUP + "/backup.sh":
        m("execute")
    elif kind == "grep" and ev[1] == SUP + "/app.log" and any("ERROR" in h for h in ev[3]):
        m("grep")
    return None


LINUX_SHELL = _lab(
    "linux-shell", "Linux Shell — Files & Permissions", "linux",
    "bash on a support server: identify the host, navigate, create files, fix permissions, run a script, search a log.",
    [
        {"id": "identify", "text": "Identify yourself and the machine (whoami, hostname)"},
        {"id": "navigate", "text": "Go to ~/support and list it with permissions (ls -l)"},
        {"id": "mkdir", "text": "Create a logs folder in ~/support"},
        {"id": "notes", "text": "Write a line to ~/support/logs/notes.txt (echo … > file)"},
        {"id": "execute", "text": "Make backup.sh executable for its owner and run it"},
        {"id": "private", "text": "Remove read access for others on report.txt, then verify with ls -l"},
        {"id": "grep", "text": "Find the ERROR line in app.log with grep"},
        {"id": "q_perm", "text": "Checkpoint: read a permission string"},
    ],
    "SR-4120 on ciwt-lnx-01: the nightly backup script won't run and an internal report is world-readable. "
    "Windows habits help: dir, cls, ipconfig and type give you the Linux equivalent. Tab completes commands and file names.",
    "Script runs, report locked down, notes written, error found — a clean Linux support session.",
    linux_state(),
    course_objectives=["IT-9.1", "IT-9.3"], minutes=25,
    rules=_linux_rules,
    hints=["whoami", "hostname", "cd ~/support", "ls -l", "mkdir logs", "echo \"checked backup\" > logs/notes.txt",
           "chmod u+x backup.sh", "./backup.sh", "chmod o-r report.txt", "ls -l", "grep ERROR app.log"],
    palette=["ls -l", "cd ", "pwd", "cat ", "chmod ", "grep ", "mkdir ", "echo ", "./", "clear", "help"],
    steps=[
        _choice("q_perm", "q_perm", "After your change ls -l shows  -rw-r-----  trainee trainee  report.txt. What does that mean?",
                ["Everyone can read and write it", "Owner can read and write, group can read, others have no access",
                 "Owner can execute it", "Only root can read it"], 1,
                {0: "Read the three triplets: rw- (owner), r-- (group), --- (others).", 2: "There is no x in the owner triplet.",
                 3: "The owner trainee can read it (rw-)."},
                right="Correct: rw- owner, r-- group, --- others.", title="Checkpoint"),
    ],
    solution={"commands": ["whoami", "hostname", "cd ~/support", "ls -l", "mkdir logs", "echo \"checked backup\" > logs/notes.txt",
                           "chmod u+x backup.sh", "./backup.sh", "chmod o-r report.txt", "ls -l", "grep ERROR app.log"],
              "answers": {"q_perm": 1}},
)

# ────────────────────────────────────────────────────────────── print-trouble


def _print_auto(state, done, cmd, lines):
    cl = cmd.lower()
    if "10.20.30.60" in cl and (cl.startswith("ping") or cl.startswith("test-connection")) and \
            not any("timed out" in ln.lower() or "failed" in ln.lower() for ln in lines):
        if "ping_printer" not in done:
            done.append("ping_printer")
    if state.get("removed_good_jobs") and not state.get("_warned_good"):
        state["_warned_good"] = True
    return None


def _print_pre(state, done, cmd):
    """cmd path for the stuck queue: net stop spooler, del ...\\spool\\PRINTERS\\*, net start spooler."""
    cl = re.sub(r"\s+", " ", (cmd or "").strip().lower())
    if not re.match(r"^(del|erase|remove-item|rm|ri)\b.*spool\\printers", cl):
        return None
    if not state.get("spooler_stopped"):
        return ["The process cannot access the file because it is being used by another process.",
                "(Stop the spooler first: net stop spooler — or prefer removing only the job in Error.)"]
    hr = next((p for p in state.get("printers") or [] if p["name"] == "HR-LaserJet"), None)
    n = len(hr["jobs"]) if hr else 0
    if hr:
        hr["jobs"] = []
    state["removed_good_jobs"] = True
    state["spooler_hung"] = False
    return [f"C:\\Windows\\System32\\spool\\PRINTERS\\*, Are you sure (Y/N)? Y", f"({n} spool files deleted.)",
            "(That cleared EVERY queued job, including the healthy Leave-form and Memo jobs — those users must resend.",
            " It is the last resort when one job can't be removed; this time Remove-PrintJob -ID 7 would have kept their work.",
            " The objective 'remove only the job in Error' can't be met in this attempt any more — Start over to practise it.)"]


PRINT_TROUBLE = _lab(
    "print-trouble", "PowerShell — Print Queue Recovery", "windows",
    "Walk the print path: printer status, network path, queue, the stuck job, spooler, verify, test page.",
    [
        {"id": "ps_shell", "text": "Start PowerShell (powershell)"},
        {"id": "get_printer", "text": "Get-Printer — find HR-LaserJet and its status"},
        {"id": "ping_printer", "text": "Test-Connection 10.20.30.60 — rule out the network path"},
        {"id": "get_jobs", "text": "Get-PrintJob -PrinterName \"HR-LaserJet\" — find the job in Error"},
        {"id": "remove_job", "text": "Remove only the job in Error (Remove-PrintJob … -ID 7)"},
        {"id": "restart_spooler", "text": "Restart-Service Spooler to release the stuck job"},
        {"id": "verify_queue", "text": "Get-PrintJob again — the healthy jobs are printing"},
        {"id": "test_page", "text": "Send a test page"},
        {"id": "q_keep", "text": "Checkpoint: what to tell the users"},
    ],
    "INC-30588: \"Nothing prints on HR-LaserJet. Three of us have sent jobs.\" The printer is at 10.20.30.60. "
    "Clear the blockage without deleting other people's work. PowerShell aliases (gsv, gps, cls) work.",
    "Queue cleared, healthy jobs kept, printer verified with a test page.",
    _win(shell="cmd", spooler_hung=True,
                   pingable_ips=["127.0.0.1", "10.20.30.1", "10.20.30.47", "10.20.30.50", "10.20.30.60"],
                   printers=[{"name": "HR-LaserJet", "driver": "HP Universal Printing PCL 6", "port": "IP_10.20.30.60",
                              "ip": "10.20.30.60", "status": "Error", "shared": True,
                              "jobs": [{"id": 7, "doc": "Payroll-Oct.xlsx", "status": "Error, Printing"},
                                       {"id": 8, "doc": "Leave-form.docx", "status": "Spooling"},
                                       {"id": 9, "doc": "Memo.pdf", "status": "Spooling"}]},
                             {"name": "Microsoft Print to PDF", "driver": "Microsoft Print To PDF", "port": "PORTPROMPT:",
                              "ip": "-", "status": "Normal", "shared": False, "jobs": []}]),
    course_objectives=["IT-4.3", "IT-13.1"], minutes=20, auto=_print_auto, pre=_print_pre,
    hints=["powershell", "Get-Printer", "Test-Connection 10.20.30.60", "Get-PrintJob -PrinterName \"HR-LaserJet\"",
           "Remove-PrintJob -PrinterName \"HR-LaserJet\" -ID 7", "Restart-Service Spooler", "Get-PrintJob -PrinterName \"HR-LaserJet\"",
           "\"test page\" | Out-Printer -Name \"HR-LaserJet\""],
    palette=["powershell", "Get-Printer", "Test-Connection ", "Get-PrintJob -PrinterName \"HR-LaserJet\"", "Remove-PrintJob -PrinterName \"HR-LaserJet\" -ID ",
             "Restart-Service Spooler", "\"test page\" | Out-Printer -Name \"HR-LaserJet\"", "cls"],
    steps=[
        _choice("q_keep", "q_keep", "Jobs 8 and 9 were healthy and are now printing. What do you tell the three users?",
                ["Everyone must print again", "Only the owner of Payroll-Oct.xlsx needs to resend; the other two jobs are printing now",
                 "Nothing — close the ticket", "Tell them to use Print to PDF from now on"], 1,
                {0: "You kept jobs 8 and 9 — only the errored job was removed.", 2: "Verify with the users before closing.",
                 3: "The printer works; that's not a fix."},
                right="Correct: only the removed job needs resending.", title="Checkpoint"),
    ],
    solution={"commands": ["powershell", "Get-Printer", "Test-Connection 10.20.30.60", "Get-PrintJob -PrinterName \"HR-LaserJet\"",
                           "Remove-PrintJob -PrinterName \"HR-LaserJet\" -ID 7", "Restart-Service Spooler",
                           "Get-PrintJob -PrinterName \"HR-LaserJet\"", "\"test page\" | Out-Printer -Name \"HR-LaserJet\""],
              "answers": {"q_keep": 1}},
)

# ────────────────────────────────────────────────────────────── rtr-vlan-acl (router on a stick + standard ACL)


def _m(done, oid):
    if oid not in done:
        done.append(oid)


def _sub_ok(ifs, name, vlan, ip):
    c = ifs.get(name) or {}
    return c.get("vlan") == vlan and c.get("ip") == ip and c.get("mask") == "255.255.255.0"


def _acl_ok(state):
    """A deny for 192.168.20.0/24 before a permit any (standard 1-99), or the extended equivalent."""
    for num, entries in (state.get("acls") or {}).items():
        es = [e for e in entries if e.get("action") != "remark"]
        if not es:
            continue
        try:
            n = int(num)
        except ValueError:
            continue
        deny_i = permit_i = None
        for i, e in enumerate(es):
            if n < 100:
                if e["action"] == "deny" and e["src"] == "192.168.20.0 0.0.0.255" and deny_i is None:
                    deny_i = i
                if e["action"] == "permit" and e["src"] == "any" and permit_i is None:
                    permit_i = i
            else:
                if e["action"] == "deny" and e["src"] == "192.168.20.0 0.0.0.255" and e["dst"] in ("10.10.10.0 0.0.0.255", "any") \
                        and deny_i is None:
                    deny_i = i
                if e["action"] == "permit" and e["src"] == "any" and e["dst"] == "any" and permit_i is None:
                    permit_i = i
        if deny_i is not None and permit_i is not None and deny_i < permit_i:
            return num
    return None


def _acl_order_issue(state):
    for num, entries in (state.get("acls") or {}).items():
        es = [e for e in entries if e.get("action") != "remark"]
        for i, e in enumerate(es):
            if e["action"] == "permit" and e.get("src") == "any" and any(x["action"] == "deny" for x in es[i + 1:]):
                return num
    return None


def _rtr_auto(state, done, cmd, lines):
    ifs = state["interfaces"]
    tips = []
    if _sub_ok(ifs, "GigabitEthernet0/0.10", 10, "192.168.10.1"):
        _m(done, "sub10")
    if _sub_ok(ifs, "GigabitEthernet0/0.20", 20, "192.168.20.1"):
        _m(done, "sub20")
    if (ifs.get("GigabitEthernet0/0") or {}).get("admin") and "sub10" in done and "sub20" in done:
        _m(done, "trunk_up")
    num = _acl_ok(state)
    if num:
        _m(done, "acl")
    bad = _acl_order_issue(state)
    if bad and cmd.lower().startswith("access-list") and not state.get("_tip_order"):
        state["_tip_order"] = True
        tips.append(f"(Lab tip: ACL {bad} has permit any ABOVE a deny. Entries are read top-down and the first match wins, so the deny is never "
                    f"reached. Remove it with: no access-list {bad} — then enter the deny first.)")
    if num:
        n = int(num)
        out_g1 = (ifs.get("GigabitEthernet0/1") or {}).get("acl_out") == num
        in_g20 = (ifs.get("GigabitEthernet0/0.20") or {}).get("acl_in") == num
        if out_g1 or (n >= 100 and in_g20):
            _m(done, "applied")
        elif n < 100 and in_g20 and not state.get("_tip_place"):
            state["_tip_place"] = True
            tips.append("(Lab tip: a standard ACL inbound on Gi0/0.20 blocks the guests from EVERYTHING, including the internet. "
                        "Standard ACLs go close to the destination: ip access-group " + num + " out on Gi0/1.)")
    if cmd.lower().startswith("show access-lists") and "acl" in done:
        _m(done, "verify_acl")
    return tips


RTR_VLAN_ACL = _lab(
    "rtr-vlan-acl", "Router — Inter-VLAN Routing & ACL", "router",
    "Router-on-a-stick for VLAN 10 (staff) and 20 (guest), then a standard ACL so guests cannot reach the server LAN.",
    [
        {"id": "enable", "text": "Enter privileged EXEC (enable)"},
        {"id": "sub10", "text": "Gi0/0.10: encapsulation dot1Q 10, 192.168.10.1/24"},
        {"id": "sub20", "text": "Gi0/0.20: encapsulation dot1Q 20, 192.168.20.1/24"},
        {"id": "trunk_up", "text": "no shutdown on the physical Gi0/0 (the trunk to the switch)"},
        {"id": "acl", "text": "ACL 10: deny 192.168.20.0 0.0.0.255, then permit any — in that order"},
        {"id": "applied", "text": "Apply it outbound toward the servers: ip access-group 10 out on Gi0/1"},
        {"id": "verify_acl", "text": "show access-lists"},
        {"id": "write", "text": "Save the configuration (write / copy run start)"},
        {"id": "q_implicit", "text": "Checkpoint: the implicit deny"},
    ],
    "CHG-1187: the switch trunks VLAN 10 (STAFF) and 20 (GUEST) to R1 Gi0/0. Servers are on Gi0/1 (10.10.10.0/24, already configured). "
    "Route between the VLANs, and stop guests reaching the servers while keeping their internet. IOS abbreviations, ? and Tab work.",
    "Inter-VLAN routing up, guest-to-server traffic denied with the ACL in the right place, configuration saved.",
    {"hostname": "R1", "mode": "user", "prompt_if": None, "acls": {},
     "interfaces": {"GigabitEthernet0/0": {"ip": None, "mask": None, "up": False, "admin": False},
                    "GigabitEthernet0/1": {"ip": "10.10.10.1", "mask": "255.255.255.0", "up": True, "admin": True}},
     "hosts": {"10.10.10.20": True, "192.168.10.50": True, "192.168.20.50": True}},
    course_objectives=["NO-2.2", "NO-4.3", "NO-5.3", "NO-9.2"], minutes=30, auto=_rtr_auto,
    hints=["enable", "configure terminal", "interface gi0/0", "no shutdown", "interface gi0/0.10", "encapsulation dot1Q 10",
           "ip address 192.168.10.1 255.255.255.0", "interface gi0/0.20", "encapsulation dot1Q 20",
           "ip address 192.168.20.1 255.255.255.0", "exit", "access-list 10 deny 192.168.20.0 0.0.0.255", "access-list 10 permit any",
           "interface gi0/1", "ip access-group 10 out", "end", "show access-lists", "write"],
    palette=["enable", "conf t", "interface ", "encapsulation dot1Q ", "ip address ", "no shutdown", "access-list 10 ",
             "ip access-group 10 out", "exit", "end", "show ip interface brief", "show access-lists", "write", "?"],
    steps=[
        _choice("q_implicit", "q_implicit", "If ACL 10 had only the deny line (no permit any), what would happen on Gi0/1 outbound?",
                ["Only guests would be blocked", "All traffic to the servers would be blocked — every ACL ends with an implicit deny any",
                 "The ACL would be ignored", "Only staff would be blocked"], 1,
                {0: "There is a hidden last line: deny any.", 2: "IOS applies it; an ACL with no permit blocks everything.",
                 3: "Staff would be blocked too — along with everyone else."},
                right="Correct: the implicit deny any at the end blocks everything not permitted.", title="Checkpoint"),
    ],
    solution={"commands": ["enable", "configure terminal", "interface gi0/0", "no shutdown", "interface gi0/0.10",
                           "encapsulation dot1Q 10", "ip address 192.168.10.1 255.255.255.0", "interface gi0/0.20",
                           "encapsulation dot1Q 20", "ip address 192.168.20.1 255.255.255.0", "exit",
                           "access-list 10 deny 192.168.20.0 0.0.0.255", "access-list 10 permit any", "interface gi0/1",
                           "ip access-group 10 out", "end", "show access-lists", "write"],
              "answers": {"q_implicit": 1}},
)

# ────────────────────────────────────────────────────────────── sw-vlan-multi


def _sw_auto(state, done, cmd, lines):
    v = {int(k): str(n).upper() for k, n in (state.get("vlans") or {}).items()}
    ifs = state["interfaces"]
    if v.get(10) == "STAFF" and v.get(20) == "GUEST":
        _m(done, "vlans")
    f2, f3, f1 = ifs.get("FastEthernet0/2", {}), ifs.get("FastEthernet0/3", {}), ifs.get("FastEthernet0/1", {})
    if f2.get("mode") == "access" and int(f2.get("vlan") or 0) == 10:
        _m(done, "port_staff")
    if f3.get("mode") == "access" and int(f3.get("vlan") or 0) == 20:
        _m(done, "port_guest")
    al = f1.get("allowed") or []
    if f1.get("mode") == "trunk" and 10 in al and 20 in al:
        _m(done, "trunk")
    c = cmd.lower()
    if c.startswith("show vlan") and {"vlans", "port_staff", "port_guest"} <= set(done):
        _m(done, "show_vlans")
    if c.startswith("show interfaces trunk") and "trunk" in done:
        _m(done, "show_trunks")
    tips = []
    if f1.get("mode") == "trunk" and al and not (10 in al and 20 in al) and c.startswith("switchport trunk allowed"):
        tips.append("(Lab tip: the allowed list must carry both 10 and 20 — e.g. switchport trunk allowed vlan 10,20)")
    return tips


SW_VLAN_MULTI = _lab(
    "sw-vlan-multi", "Switch — Multi-VLAN & Pruned Trunk", "switch",
    "Create STAFF (10) and GUEST (20), assign access ports, trunk Fa0/1 carrying only 10 and 20, verify, save.",
    [
        {"id": "enable", "text": "Enter privileged EXEC (enable)"},
        {"id": "vlans", "text": "Create VLAN 10 named STAFF and VLAN 20 named GUEST"},
        {"id": "port_staff", "text": "Fa0/2: access port in VLAN 10"},
        {"id": "port_guest", "text": "Fa0/3: access port in VLAN 20"},
        {"id": "trunk", "text": "Fa0/1: trunk to R1 allowing only VLANs 10,20"},
        {"id": "show_vlans", "text": "Verify with show vlan brief"},
        {"id": "show_trunks", "text": "Verify with show interfaces trunk"},
        {"id": "write", "text": "Save the configuration"},
    ],
    "CHG-1186 (pairs with the router lab): Fa0/1 goes to R1, Fa0/2 to a staff PC, Fa0/3 to the guest kiosk. "
    "Abbreviations (vl, sw mo ac, sh vl br), ? and Tab work.",
    "VLANs, access ports and a pruned trunk are configured, verified and saved.",
    {"hostname": "SW-ACCESS-01", "mode": "user", "prompt_if": None, "edit_vlan": None, "vlans": {1: "default"},
     "interfaces": {"FastEthernet0/1": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
                    "FastEthernet0/2": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
                    "FastEthernet0/3": {"mode": "access", "vlan": 1, "up": True, "trunk": False}}},
    course_objectives=["NO-2.2", "NO-9.1"], minutes=20, auto=_sw_auto,
    hints=["enable", "configure terminal", "vlan 10", "name STAFF", "vlan 20", "name GUEST", "interface fa0/2",
           "switchport mode access", "switchport access vlan 10", "interface fa0/3", "switchport mode access",
           "switchport access vlan 20", "interface fa0/1", "switchport mode trunk", "switchport trunk allowed vlan 10,20", "end",
           "show vlan brief", "show interfaces trunk", "write"],
    palette=["enable", "conf t", "vlan ", "name ", "interface ", "switchport mode access", "switchport access vlan ",
             "switchport mode trunk", "switchport trunk allowed vlan 10,20", "end", "show vlan brief", "show interfaces trunk", "write", "?"],
    solution={"commands": ["enable", "configure terminal", "vlan 10", "name STAFF", "vlan 20", "name GUEST", "interface fa0/2",
                           "switchport mode access", "switchport access vlan 10", "interface fa0/3", "switchport mode access",
                           "switchport access vlan 20", "interface fa0/1", "switchport mode trunk",
                           "switchport trunk allowed vlan 10,20", "end", "show vlan brief", "show interfaces trunk", "write"]},
)

# ────────────────────────────────────────────────────────────── wifi-secure (SOHO router admin page)


def _on(a, k):
    return str(a.get(k, "")).lower() in ("on", "true", "1", "yes")


WIFI_SECURE = _lab(
    "wifi-secure", "SOHO Router & Wi-Fi Hardening", "activity",
    "Harden a small-office router: admin password, firmware, remote management, WPA3, passphrase, WPS, channel, guest isolation.",
    [
        {"id": "harden", "text": "Lock down the router's own management"},
        {"id": "wlan", "text": "Secure the staff wireless network"},
        {"id": "guest", "text": "Set up an isolated guest network"},
        {"id": "why_wps", "text": "Checkpoint: why WPS is turned off"},
    ],
    "Dental office (8 staff, all devices from 2022 or newer). A neighbour Wi-Fi survey shows channels 1 and 11 busy on 2.4 GHz. "
    "Visitors in the waiting room need internet only. Change each setting, then Save — the router tells you what still fails policy.",
    "Router hardened: management locked, WPA3 with a strong passphrase, WPS off, clean channel, isolated guests.",
    {"kind": "activity"},
    course_objectives=["IT-5.4", "NO-3.3", "NO-5.2"], minutes=20,
    steps=[
        {"id": "w1", "type": "config", "objective": "harden", "title": "Administration",
         "prompt": "Router ▸ Administration", "submit_label": "Save",
         "fields": [
             {"name": "admin_password", "label": "Admin password", "kind": "password", "default": "admin",
              "help": "Factory default is admin."},
             {"name": "firmware", "label": "Firmware", "kind": "select", "default": "keep",
              "options": [["keep", "Keep 1.0.4 (installed)"], ["install", "Install 1.2.1 (security update available)"]]},
             {"name": "remote_mgmt", "label": "Remote management from the internet (WAN)", "kind": "toggle", "default": "on"},
             {"name": "upnp", "label": "UPnP", "kind": "toggle", "default": "on"},
         ],
         "rules": [
             ("admin_password", lambda a: len(a.get("admin_password", "")) >= 12 and a.get("admin_password") != "admin",
              "Admin password: change the default to a unique password of 12+ characters."),
             ("firmware", lambda a: a.get("firmware") == "install", "Firmware: install the security update."),
             ("remote_mgmt", lambda a: not _on(a, "remote_mgmt"), "Remote management: turn it off — the admin page should not face the internet."),
             ("upnp", lambda a: not _on(a, "upnp"), "UPnP: turn it off — it lets devices open inbound ports without you knowing."),
         ]},
        {"id": "w2", "type": "config", "objective": "wlan", "title": "Wireless (staff)",
         "prompt": "Router ▸ Wireless ▸ Staff network", "submit_label": "Save",
         "fields": [
             {"name": "ssid", "label": "Network name (SSID)", "kind": "text", "default": "NETGEAR-3F2A"},
             {"name": "security", "label": "Security", "kind": "select", "default": "wpa2tkip",
              "options": [["open", "None (open)"], ["wep", "WEP"], ["wpa2tkip", "WPA2-Personal (TKIP)"], ["wpa2aes", "WPA2-Personal (AES)"],
                          ["wpa23", "WPA2/WPA3-Personal (transition)"], ["wpa3", "WPA3-Personal (SAE)"]]},
             {"name": "passphrase", "label": "Passphrase", "kind": "password", "default": "password123"},
             {"name": "wps", "label": "WPS (push-button / PIN)", "kind": "toggle", "default": "on"},
             {"name": "channel", "label": "2.4 GHz channel", "kind": "select", "default": "11",
              "options": [["1", "1"], ["3", "3"], ["6", "6"], ["11", "11"]]},
         ],
         "rules": [
             ("ssid", lambda a: a.get("ssid", "").strip() and a.get("ssid", "").strip().upper() != "NETGEAR-3F2A",
              "SSID: change the default name (it reveals the router model)."),
             ("security", lambda a: a.get("security") == "wpa3",
              "Security: every device supports WPA3, so use WPA3-Personal (transition mode is only for devices that can't)."),
             ("passphrase", lambda a: len(a.get("passphrase", "")) >= 15 and a.get("passphrase", "").lower() not in ("password123",)
              and a.get("ssid", "").lower() not in a.get("passphrase", "").lower(),
              "Passphrase: at least 15 characters, not the default, and not containing the SSID."),
             ("wps", lambda a: not _on(a, "wps"), "WPS: turn it off."),
             ("channel", lambda a: a.get("channel") == "6", "Channel: 1 and 11 are busy — the remaining non-overlapping channel is 6."),
         ]},
        {"id": "w3", "type": "config", "objective": "guest", "title": "Guest network",
         "prompt": "Router ▸ Wireless ▸ Guest network", "submit_label": "Save",
         "fields": [
             {"name": "guest", "label": "Guest network", "kind": "toggle", "default": "off"},
             {"name": "isolation", "label": "Client isolation / no access to local network", "kind": "toggle", "default": "off"},
             {"name": "guest_pass", "label": "Guest passphrase", "kind": "password", "default": ""},
         ],
         "rules": [
             ("guest", lambda a: _on(a, "guest"), "Guest network: turn it on so visitors stay off the staff network."),
             ("isolation", lambda a: _on(a, "isolation"), "Isolation: turn it on — visitors need the internet, not the X-ray PCs."),
             ("guest_pass", lambda a: len(a.get("guest_pass", "")) >= 12, "Guest passphrase: 12+ characters, different from staff."),
         ]},
        _choice("w4", "why_wps", "Why is WPS turned off?",
                ["It slows the Wi-Fi down", "Its PIN method can be brute-forced, giving the passphrase to an attacker",
                 "It is required for WPA3", "It disables the guest network"], 1,
                {0: "Speed isn't the issue.", 2: "WPA3 doesn't need WPS.", 3: "Unrelated."},
                right="Correct: WPS PINs can be brute-forced in hours.", title="Checkpoint"),
    ],
    obj_hints={
        "harden": ["Four settings: password, firmware, remote management, UPnP.", "Unique 12+ char admin password, install firmware 1.2.1, remote management off, UPnP off."],
        "wlan": ["All devices are recent; neighbours use 1 and 11.", "New SSID, WPA3-Personal, 15+ character passphrase, WPS off, channel 6."],
        "guest": ["Visitors: internet only.", "Guest on, isolation on, separate 12+ character passphrase."],
        "why_wps": ["Think about the 8-digit PIN.", "The PIN can be brute-forced."],
    },
    solution={"answers": {
        "w1": {"admin_password": "Harbour-Lantern-2026!", "firmware": "install", "remote_mgmt": "off", "upnp": "off"},
        "w2": {"ssid": "SmileDental-Staff", "security": "wpa3", "passphrase": "copper kettle orbit maple", "wps": "off", "channel": "6"},
        "w3": {"guest": "on", "isolation": "on", "guest_pass": "waiting-room-guests"}, "w4": 1}},
)

# ────────────────────────────────────────────────────────────── sec-malware

MALWARE_STEPS = ["Investigate and verify the malware symptoms", "Quarantine the infected system", "Disable System Restore",
                 "Remediate: update anti-malware, scan and remove (Safe Mode / offline scan)", "Schedule scans and run updates",
                 "Enable System Restore and create a restore point", "Educate the end user"]

SEC_MALWARE = _lab(
    "sec-malware", "Malware Incident Response", "activity",
    "Order the removal steps, then make the in-role decisions: quarantine, restore points, remediation, ransomware escalation.",
    [
        {"id": "order", "text": "Put the malware removal steps in order"},
        {"id": "quarantine", "text": "Choose how to quarantine"},
        {"id": "restore", "text": "Explain why System Restore is disabled"},
        {"id": "remediate", "text": "Pick remediation actions that stay within the support role"},
        {"id": "escalate", "text": "Recognise when it's a security incident, not a ticket"},
    ],
    "INC-30611: Sam's PC shows pop-ups, the browser home page changed, and Defender real-time protection is off.",
    "Malware handled in order, inside your role, with escalation when it becomes an incident.",
    {"kind": "activity"},
    course_objectives=["IT-10.2", "IT-10.4"], minutes=15,
    steps=[
        {"id": "x1", "type": "order", "objective": "order", "title": "Removal process", "items": MALWARE_STEPS,
         "prompt": "Put the seven steps in order.",
         "tips": {MALWARE_STEPS[1]: "Stop the spread before anything else changes on the PC.",
                  MALWARE_STEPS[2]: "Restore points are turned off before you clean, so they can't re-infect.",
                  MALWARE_STEPS[5]: "Restore is turned back on only after the system is clean and updated.",
                  MALWARE_STEPS[6]: "User education is the last step."}},
        _choice("x2", "quarantine", "How do you quarantine Sam's PC?",
                ["Leave it on the network so Defender can update", "Disconnect it from the network (unplug Ethernet, turn off Wi-Fi) and stop using shared drives",
                 "Shut it down and re-image immediately", "Email the suspicious file to IT for analysis"], 1,
                {0: "Update definitions offline or after cleaning; first stop the spread.", 2: "Re-imaging first destroys evidence and skips the process.",
                 3: "Never forward malware by email."},
                right="Correct: isolate from the network first."),
        _choice("x3", "restore", "Why disable System Restore before cleaning?",
                ["It speeds up the scan", "Restore points can contain the malware and re-infect the PC after cleaning",
                 "It is required to boot Safe Mode", "It frees disk space for the scanner"], 1,
                right="Correct: infected restore points are removed so they can't bring it back."),
        _choice("x4", "remediate", "Which remediation actions are within the help-desk role? (choose all that apply)",
                ["Update anti-malware definitions", "Run a full / offline scan from Safe Mode or Windows Security (Microsoft Defender Offline)",
                 "Record findings in the ticket and notify security per policy", "Turn Defender off permanently so the pop-ups stop",
                 "Copy the infected files to a USB stick to look at them at home"], [0, 1, 2],
                {3: "Never weaken protection.", 4: "Removing data or malware from the site is a policy breach."}, multi=True,
                right="Correct."),
        _choice("x5", "escalate", "While you work, a ransom note appears and files on the shared drive start getting renamed .locked. What now?",
                ["Keep scanning — finish the removal process", "Pay the ransom to save the files",
                 "Stop, keep the PC isolated (don't wipe it), and escalate immediately to the security incident team with times and what you saw",
                 "Restore the share from last night's backup yourself"], 2,
                {0: "This is now a security incident; the removal checklist stops here.", 1: "Never — and it is not your decision.",
                 3: "Restoring before containment can re-encrypt the restore and destroys evidence; the incident team leads."},
                right="Correct: contain, preserve, escalate."),
    ],
    obj_hints={
        "order": ["Verify, then stop the spread.", "Investigate → Quarantine → Disable Restore → Remediate → Schedule/Update → Enable Restore → Educate."],
        "quarantine": ["Stop it spreading.", "Disconnect from the network."],
        "restore": ["Where can malware hide?", "In restore points."],
        "remediate": ["Three are within role.", "Update definitions, offline/Safe Mode scan, record and notify."],
        "escalate": ["Is this still a help-desk ticket?", "Contain, preserve, escalate to the incident team."],
    },
    solution={"answers": {"x1": MALWARE_STEPS, "x2": 1, "x3": 1, "x4": [0, 1, 2], "x5": 2}},
)

# ────────────────────────────────────────────────────────────── ops-backup


def _num(want, why):
    def chk(got, vals, ans):
        s = str(got).strip().lower().replace("hours", "").replace("hour", "").replace("h", "").strip()
        try:
            return float(s) == float(want), why
        except ValueError:
            return False, 'enter a number of hours.'
    return chk


OPS_BACKUP = _lab(
    "ops-backup", "Backup & Restore Planning", "activity",
    "Match backup types, work out which sets a restore needs, check a plan against 3-2-1, set RPO/RTO and prove it with a test restore.",
    [
        {"id": "types", "text": "Match backup types and snapshots to what they do"},
        {"id": "restore_inc", "text": "Restore sets with incremental backups"},
        {"id": "restore_diff", "text": "Restore sets with differential backups"},
        {"id": "rule321", "text": "Recognise a 3-2-1 plan"},
        {"id": "rpo", "text": "Turn business requirements into RPO and RTO"},
        {"id": "test_restore", "text": "Prove the backup works"},
    ],
    "SR-4188: the office manager asks whether the file server's backups would actually save them. Show your working.",
    "You can choose a backup scheme, say what a restore needs, and prove it with a test restore.",
    {"kind": "activity"},
    course_objectives=["IT-12.3", "IT-3.2"], minutes=20,
    steps=[
        {"id": "k1", "type": "match", "objective": "types", "title": "Backup types",
         "prompt": "Match each description to its type.",
         "items": [{"id": "d_full", "label": "Copies everything selected; slowest job, simplest restore", "answer": "full"},
                   {"id": "d_inc", "label": "Copies changes since the last backup of any kind; smallest nightly job", "answer": "inc"},
                   {"id": "d_diff", "label": "Copies changes since the last full; grows each day", "answer": "diff"},
                   {"id": "d_snap", "label": "Point-in-time copy on the same storage — quick rollback, not a backup on its own", "answer": "snap"},
                   {"id": "d_raid", "label": "Keeps running when one disk dies, but deleted files are deleted on every disk", "answer": "raid",
                    "tip": "RAID is availability, not backup."}],
         "targets": [{"id": "full", "label": "Full"}, {"id": "inc", "label": "Incremental"}, {"id": "diff", "label": "Differential"},
                     {"id": "snap", "label": "Snapshot"}, {"id": "raid", "label": "RAID 1/5"}]},
        _choice("k2", "restore_inc", "Full backup Sunday night, incrementals Monday–Thursday nights. The disk dies Friday morning. Which sets do you restore? (all that apply)",
                ["Sunday full", "Monday incremental", "Tuesday incremental", "Wednesday incremental", "Thursday incremental"], [0, 1, 2, 3, 4],
                multi=True, right="Correct: the full plus every incremental, in order."),
        _choice("k3", "restore_diff", "Same week, but with differentials Monday–Thursday. Which sets do you restore? (all that apply)",
                ["Sunday full", "Monday differential", "Tuesday differential", "Wednesday differential", "Thursday differential"], [0, 4],
                {1: "Each differential already includes Monday's changes — you only need the latest one.",
                 2: "Only the latest differential is needed.", 3: "Only the latest differential is needed."},
                multi=True, right="Correct: the full plus the latest differential."),
        _choice("k4", "rule321", "Which plan meets the 3-2-1 rule?",
                ["The server's RAID 5 array plus a nightly snapshot on the same array",
                 "Production data, a nightly backup to a NAS in the office, and an encrypted copy to cloud storage",
                 "Two USB drives kept in the server room", "A weekly full backup to the same disk"], 1,
                {0: "One device, one site — snapshots and RAID don't count as separate copies.",
                 2: "Only two copies, both on site.", 3: "Same disk: one failure loses both."},
                right="Correct: 3 copies, 2 media, 1 off site."),
        {"id": "k5", "type": "fields", "objective": "rpo", "title": "RPO / RTO",
         "prompt": "The business can lose at most 4 hours of work and needs the file server back within 8 hours of a failure.",
         "fields": [{"name": "rpo", "label": "RPO (hours)", "inputmode": "decimal", "check": _num(4, 'RPO = how much data loss is acceptable.')},
                    {"name": "rto", "label": "RTO (hours)", "inputmode": "decimal", "check": _num(8, 'RTO = how long until service is back.')},
                    {"name": "every", "label": "Back up at least every … hours", "inputmode": "decimal",
                     "check": _num(4, 'the backup interval cannot be longer than the RPO.')}]},
        _choice("k6", "test_restore", "How do you prove the backups work?",
                ["The backup software shows green ticks", "Do a test restore to an alternate location and open the files; record the time it took",
                 "Check the backup drive is full", "Ask the vendor"], 1,
                {0: "A successful job doesn't prove the data restores.", 2: "Full means nothing about integrity."},
                right="Correct: a timed test restore proves both the data and the RTO."),
    ],
    obj_hints={
        "types": ["Since last FULL vs since last ANY backup.", "Incremental = since any; differential = since full; snapshot and RAID are not backups."],
        "restore_inc": ["Each incremental only has one day.", "You need all five."],
        "restore_diff": ["Each differential has everything since the full.", "Sunday full + Thursday differential."],
        "rule321": ["3 copies, 2 media types, 1 off site.", "Production + office NAS + cloud copy."],
        "rpo": ["RPO is data loss, RTO is downtime.", "RPO 4, RTO 8, back up every 4 hours (or more often)."],
        "test_restore": ["Prove it, don't assume it.", "Timed test restore to an alternate location."],
    },
    solution={"answers": {"k1": {"d_full": "full", "d_inc": "inc", "d_diff": "diff", "d_snap": "snap", "d_raid": "raid"},
                          "k2": [0, 1, 2, 3, 4], "k3": [0, 4], "k4": 1, "k5": {"rpo": "4", "rto": "8", "every": "4"}, "k6": 1}},
)

# ────────────────────────────────────────────────────────────── virt-vm

VIRT_VM = _lab(
    "virt-vm", "Virtualization — VM Provisioning", "activity",
    "Configure a Windows 11 guest (UEFI, Secure Boot, vTPM, CPU/RAM/disk, NAT), then snapshots vs backups and a VT-x fault.",
    [
        {"id": "vm_config", "text": "Configure the VM to meet Windows 11 and the network brief"},
        {"id": "snap_backup", "text": "Explain why a snapshot is not a backup"},
        {"id": "vtx", "text": "Fix a VM that won't start"},
    ],
    "SR-4201: build a Windows 11 VM for testing a new app. Host: 8 cores, 16 GB RAM, 500 GB free. The VM must download updates "
    "but must NOT be reachable from the classroom LAN. Take a baseline snapshot so the test can be rolled back.",
    "VM built to spec with a baseline snapshot; you know a snapshot's limits and how to fix a host-side VT-x fault.",
    {"kind": "activity"},
    course_objectives=["IT-6.1", "IT-6.3", "IT-8.1"], minutes=15,
    steps=[
        {"id": "v1", "type": "config", "objective": "vm_config", "title": "New virtual machine",
         "prompt": "Hypervisor ▸ New virtual machine", "submit_label": "Create VM",
         "fields": [
             {"name": "firmware", "label": "Firmware / generation", "kind": "select", "default": "bios",
              "options": [["bios", "BIOS (Generation 1)"], ["uefi", "UEFI (Generation 2)"]]},
             {"name": "secure_boot", "label": "Secure Boot", "kind": "toggle", "default": "off"},
             {"name": "tpm", "label": "Trusted Platform Module", "kind": "select", "default": "none",
              "options": [["none", "None"], ["vtpm", "Virtual TPM 2.0"]]},
             {"name": "vcpu", "label": "Virtual processors", "kind": "select", "default": "1", "options": [["1", "1"], ["2", "2"], ["4", "4"], ["8", "8"]]},
             {"name": "ram", "label": "Memory (GB)", "kind": "select", "default": "2",
              "options": [["2", "2"], ["4", "4"], ["8", "8"], ["16", "16"]]},
             {"name": "disk", "label": "Virtual disk (GB)", "kind": "select", "default": "32",
              "options": [["32", "32"], ["64", "64"], ["128", "128"]]},
             {"name": "network", "label": "Network adapter", "kind": "select", "default": "bridged",
              "options": [["bridged", "Bridged (on the classroom LAN)"], ["nat", "NAT (internet via the host)"],
                          ["host", "Host-only"], ["none", "Not connected"]]},
             {"name": "snapshot", "label": "Take snapshot \"baseline\" after setup", "kind": "toggle", "default": "off"},
         ],
         "rules": [
             ("firmware", lambda a: a.get("firmware") == "uefi", "Firmware: Windows 11 needs UEFI (Generation 2)."),
             ("secure_boot", lambda a: _on(a, "secure_boot"), "Secure Boot: Windows 11 requires it to be available — turn it on."),
             ("tpm", lambda a: a.get("tpm") == "vtpm", "TPM: add a virtual TPM 2.0."),
             ("vcpu", lambda a: int(a.get("vcpu") or 0) >= 2 and int(a.get("vcpu") or 0) <= 4,
              "Processors: Windows 11 needs 2+; don't give a guest all 8 host cores."),
             ("ram", lambda a: 4 <= int(a.get("ram") or 0) <= 8, "Memory: at least 4 GB, and leave the host enough (16 GB host — not all of it)."),
             ("disk", lambda a: int(a.get("disk") or 0) >= 64, "Disk: Windows 11 needs 64 GB or more."),
             ("network", lambda a: a.get("network") == "nat", "Network: NAT gives internet without exposing the VM on the classroom LAN."),
             ("snapshot", lambda a: _on(a, "snapshot"), "Snapshot: take the baseline so the test can be rolled back."),
         ]},
        _choice("v2", "snap_backup", "Why isn't the \"baseline\" snapshot a backup?",
                ["Snapshots are compressed", "It depends on the VM's own disk files on the same host — lose the host or its disk and the snapshot goes too",
                 "Snapshots expire after 24 hours", "It is a backup"], 1,
                right="Correct: a snapshot is a rollback point on the same storage."),
        _choice("v3", "vtx", "A colleague's VM won't start: \"VT-x is disabled in the BIOS for all CPU modes\". What fixes it?",
                ["Give the VM more RAM", "Enable Intel VT-x / AMD-V (SVM) in the HOST's UEFI setup", "Reinstall the guest OS",
                 "Switch the VM to Bridged networking"], 1,
                {0: "Memory isn't the issue.", 2: "The guest never starts — the fault is on the host.", 3: "Unrelated."},
                right="Correct: hardware virtualization is a host firmware setting."),
    ],
    obj_hints={
        "vm_config": ["Windows 11: UEFI, Secure Boot, TPM 2.0, 2 CPUs, 4 GB, 64 GB.", "UEFI, Secure Boot on, vTPM, 2-4 vCPU, 4-8 GB, 64 GB+, NAT, snapshot on."],
        "snap_backup": ["Where does the snapshot live?", "On the same host/disk as the VM."],
        "vtx": ["Is it the guest or the host?", "Enable VT-x/AMD-V in the host firmware."],
    },
    solution={"answers": {"v1": {"firmware": "uefi", "secure_boot": "on", "tpm": "vtpm", "vcpu": "2", "ram": "8", "disk": "64",
                                 "network": "nat", "snapshot": "on"}, "v2": 1, "v3": 1}},
)

# ────────────────────────────────────────────────────────────── mob-mdm

MOB_MDM = _lab(
    "mob-mdm", "Mobile Device & MDM Triage", "activity",
    "Work three phone tickets: Wi-Fi vs cellular isolation, a compliance block from MDM, and a lost device.",
    [
        {"id": "isolate", "text": "Isolate a mobile connectivity fault"},
        {"id": "compliance", "text": "Resolve an MDM compliance block without bypassing policy"},
        {"id": "lost", "text": "Handle a lost managed phone in the right order"},
        {"id": "byod", "text": "Know what MDM can and can't do on a personal (BYOD) phone"},
    ],
    "Three tickets from the sales team's managed phones. Each answer explains why.",
    "Mobile tickets handled inside policy.",
    {"kind": "activity"},
    course_objectives=["IT-4.2", "IT-1.4"], minutes=10,
    steps=[
        _choice("p1", "isolate", "Alex's phone loads nothing on office Wi-Fi but works on 5G. Colleagues' phones work on the same Wi-Fi. Best next check?",
                ["Factory-reset the phone", "Forget and rejoin the office network, and check the phone's Wi-Fi IP (169.254? wrong SSID? private MAC blocked?)",
                 "Call the mobile carrier", "Replace the office access point"], 1,
                {0: "Far too disruptive this early.", 2: "Cellular works — the carrier is fine.", 3: "Other phones work on it."},
                right="Correct: scope is this phone on this network — check its Wi-Fi join and address."),
        _choice("p2", "compliance", "Jordan can't open company email: \"Device not compliant — OS update required\". Jordan asks you to exclude the phone from the policy. What do you do?",
                ["Add Jordan to the policy exclusion group", "Help Jordan install the pending OS update, then sync the device in the Company Portal / MDM app",
                 "Remove MDM so email works", "Set up email forwarding to Jordan's personal address"], 1,
                {0: "That bypasses a security control; only the policy owner can approve exceptions.", 2: "Removing management removes access — and breaks policy.",
                 3: "Forwarding company mail to personal accounts is a data-protection breach."},
                right="Correct: fix the compliance reason, then re-check compliance."),
        {"id": "p3", "type": "order", "objective": "lost", "title": "Lost phone",
         "prompt": "Sam left a managed phone in a taxi. Put the actions in order.",
         "items": ["Verify the caller is Sam (identity check)", "Mark the device lost / lock it remotely in MDM and show a contact message",
                   "Revoke sessions and reset the account password with Sam", "Remote wipe if not recovered within the policy window",
                   "Record times and actions in the ticket"],
         "tips": {"Verify the caller is Sam (identity check)": "Anyone can phone in claiming a lost device — verify first."}},
        _choice("p4", "byod", "On Riley's PERSONAL phone (BYOD, work profile only), what can IT see or do?",
                ["Read Riley's personal photos and texts", "Wipe the work profile and its apps/data only, and see device model, OS version and compliance",
                 "Track Riley's location at all times", "Wipe the whole phone whenever IT wants"], 1,
                right="Correct: BYOD management is limited to the work profile."),
    ],
    obj_hints={
        "isolate": ["Who else is affected, and on which network?", "Rejoin Wi-Fi and check the phone's IP/SSID/MAC settings."],
        "compliance": ["Don't bypass a control.", "Install the update, then sync with MDM."],
        "lost": ["Identity first.", "Verify → Lock/lost mode → Revoke & reset → Wipe if not found → Record."],
        "byod": ["Work profile only.", "Wipe the work profile; see model/OS/compliance."],
    },
    solution={"answers": {"p1": 1, "p2": 1, "p3": ["Verify the caller is Sam (identity check)",
                                                     "Mark the device lost / lock it remotely in MDM and show a contact message",
                                                     "Revoke sessions and reset the account password with Sam",
                                                     "Remote wipe if not recovered within the policy window", "Record times and actions in the ticket"],
                          "p4": 1}},
)

# ────────────────────────────────────────────────────────────── win-ad-users (Win11 GUI + ADUC)


def _ad(st):
    return st.get("ad") or {}


def _u(st, sam):
    return next((u for u in _ad(st).get("users", []) if u["sam"] == sam), None)


AD_RULES = {
    "open_aduc": "open:aduc",
    "create_user": lambda st, ev, d: bool((lambda u: u and u["ou"] == "Sales" and u["name"].lower() == "maria lopez" and u["must_change"])
                                          (_u(st, "mlopez"))),
    "add_group": lambda st, ev, d: bool((lambda u: u and "Sales-Staff" in u["groups"] and not any(g in u["groups"] for g in ("Domain Admins",)))
                                        (_u(st, "mlopez"))),
    "unlock": lambda st, ev, d: bool((lambda u: u and not u["locked"])(_u(st, "jchen"))),
    "reset_pw": lambda st, ev, d: bool((lambda u: u and u["pw_reset"] and u["must_change"])(_u(st, "jchen"))),
    "disable": lambda st, ev, d: bool((lambda u: u and not u["enabled"])(_u(st, "rpatel"))),
}

WIN_AD_USERS = _lab(
    "win-ad-users", "Active Directory User Lifecycle", "win11gui",
    "ADUC on a Windows 11 admin workstation: create a user in the right OU, least-privilege group, unlock and reset, disable a leaver.",
    [
        {"id": "open_aduc", "text": "Open Active Directory Users and Computers (Start → search \"dsa\" or \"Active Directory\")"},
        {"id": "create_user", "text": "Create Maria Lopez (mlopez) in the Sales OU, must change password at next logon"},
        {"id": "add_group", "text": "Add mlopez to Sales-Staff (least privilege)"},
        {"id": "unlock", "text": "Unlock Jamie Chen (jchen)"},
        {"id": "reset_pw", "text": "Reset jchen's password with \"must change at next logon\" (after verifying identity)"},
        {"id": "disable", "text": "Disable Ravi Patel (rpatel) — a leaver; do not delete"},
    ],
    "Three tickets from training.local: REQ-2231 new starter Maria Lopez (Sales); INC-30655 Jamie Chen locked out — identity verified "
    "by call-back to the number on file; HR-4471 Ravi Patel left on Friday. Domain policy: passwords 14+ characters.",
    "Onboarded, unlocked and offboarded with least privilege and the domain's password policy.",
    {"gui": None},
    course_objectives=["IT-10.1", "IT-8.4", "IT-1.4"], minutes=20, gui_rules=AD_RULES, gui_ad=True,
    hints=["Start → type dsa (Active Directory Users and Computers)", "Select the Sales OU → New user",
           "Right-click (or long-press) mlopez → Add to a group → Sales-Staff", "jchen → Unlock account",
           "jchen → Reset password (tick must change)", "rpatel → Disable account"],
    obj_hints={
        "open_aduc": ["Search the Start menu.", "Start → type dsa → Active Directory Users and Computers."],
        "create_user": ["The OU decides policies — pick Sales.", "Sales OU → New user: Maria / Lopez / mlopez, 14+ char password, tick must change."],
        "add_group": ["Least privilege: department group only.", "mlopez → Add to group → Sales-Staff."],
        "unlock": ["jchen is in Sales.", "jchen → Unlock account."],
        "reset_pw": ["Identity was verified by call-back.", "jchen → Reset password, 14+ characters, tick must change."],
        "disable": ["Leavers are disabled, not deleted.", "rpatel (HR OU) → Disable account."],
    },
    solution={"events": [
        ("open:aduc", {}),
        ("ad:create", {"first": "Maria", "last": "Lopez", "sam": "mlopez", "ou": "Sales", "password": "Granite-Window-Lake-42",
                       "confirm": "Granite-Window-Lake-42", "must_change": True}),
        ("ad:addgroup", {"sam": "mlopez", "group": "Sales-Staff"}),
        ("ad:unlock", {"sam": "jchen"}),
        ("ad:reset", {"sam": "jchen", "password": "Orbit-Copper-Maple-77", "confirm": "Orbit-Copper-Maple-77", "must_change": True}),
        ("ad:disable", {"sam": "rpatel"}),
    ]},
)


# ────────────────────────────────────────────────────────────── win-laptop-ports (ITSUP ch4–6 gaps from pass 10)

_BATT_REPORT = [
    "BATTERY REPORT — LT-0442 (Dell Latitude 5440)            generated 10/16/2026 16:02",
    "",
    "INSTALLED BATTERIES",
    "  NAME               DELL 4M1JN35",
    "  CHEMISTRY          LiP",
    "  DESIGN CAPACITY    54,000 mWh",
    "  FULL CHARGE CAPACITY 30,240 mWh",
    "  CYCLE COUNT        812",
    "",
    "BATTERY CAPACITY HISTORY",
    "  2025-10-13   53,410 mWh",
    "  2026-04-13   41,880 mWh",
    "  2026-10-13   30,240 mWh",
    "",
    "Technician note from the user: \"it dies by lunch and the touchpad feels raised\".",
]


def _wlp_pre(state, done, cmd):
    """Commands this lab adds to the Windows simulator (returns None to fall through to the shared engine)."""
    c = re.sub(r"\s+", " ", (cmd or "").strip())
    cl = c.lower()

    def mark(o):
        if o not in done:
            done.append(o)
    if cl in ("systeminfo", "systeminfo.exe"):
        mark("vm_check")
        return ["Host Name:                 " + state.get("hostname", "CIWT-W11-07"),
                "OS Name:                   Microsoft Windows 11 Pro", "OS Version:                10.0.26200 N/A Build 26200",
                "System Manufacturer:       Microsoft Corporation", "System Model:              Virtual Machine",
                "System Type:               x64-based PC", "Total Physical Memory:     8,192 MB", "Domain:                    training.local",
                "Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed."]
    if cl.startswith("powercfg"):
        if "/batteryreport" in cl or "-batteryreport" in cl:
            state["tried_batt"] = True
            return ["Unable to perform operation. An unexpected error (0x10d2) has occurred: The library, drive, or media pool is empty.",
                    "(This VM has no battery — exactly what powercfg reports on a desktop or VM. The user's laptop report",
                    " was attached to the ticket: C:\\Tickets\\battery-report-LT-0442.txt)"]
        return ["powercfg /batteryreport   — battery health report (laptops)", "powercfg /energy          — power efficiency diagnostics",
                "powercfg /a               — available sleep states"]
    if cl in ("dir c:\\tickets", "ls c:\\tickets", "gci c:\\tickets", "get-childitem c:\\tickets", "cd c:\\tickets"):
        return [" Directory of C:\\Tickets", "", "10/16/2026  04:02 PM             1,214 battery-report-LT-0442.txt"]
    m = re.match(r"^(type|cat|gc|get-content|more)\s+\"?(c:\\tickets\\)?battery-report-lt-0442\.txt\"?$", cl)
    if m:
        if state.get("tried_batt"):
            mark("battery")
        else:
            return _BATT_REPORT + ["", "(Also run powercfg /batteryreport yourself first — that is how you get this report on a laptop.)"]
        return list(_BATT_REPORT)
    if re.match(r"^nslookup (-type=mx|-q=mx|-querytype=mx) ciwt\.local", cl) or \
            re.match(r"^resolve-dnsname ciwt\.local -type mx", cl) or re.match(r"^resolve-dnsname -type mx ciwt\.local", cl):
        mark("mx")
        if cl.startswith("resolve"):
            return ["Name                 Type   TTL   Section    NameExchange          Preference",
                    "----                 ----   ---   -------    ------------          ----------",
                    "ciwt.local           MX     3600  Answer     mail.ciwt.local       10",
                    "ciwt.local           MX     3600  Answer     mail2.ciwt.local      20"]
        return ["Server:  dc01.training.local", "Address:  10.20.30.10", "",
                "ciwt.local      MX preference = 10, mail exchanger = mail.ciwt.local",
                "ciwt.local      MX preference = 20, mail exchanger = mail2.ciwt.local", "mail.ciwt.local internet address = 10.20.40.25"]
    if cl.startswith("nslookup ") and "mx" not in cl and "ciwt.local" in cl:
        return ["Server:  dc01.training.local", "Address:  10.20.30.10", "", "Name:    ciwt.local", "Address:  10.20.40.5",
                "(That is the A record. Mail servers are listed in MX records: nslookup -type=MX ciwt.local)"]
    m = re.match(r"^(test-netconnection|tnc)\s+(\S+)(?:\s+-port\s+(\d+))?(?:\s+-informationlevel\s+\S+)?$", cl)
    if m:
        host, port = m.group(2), m.group(3)
        known = {"mail.ciwt.local": "10.20.40.25", "mail2.ciwt.local": "10.20.40.26", "ciwt.local": "10.20.40.5"}
        if host not in known:
            return [f"WARNING: Name resolution of {host} failed", "", f"ComputerName   : {host}", "RemoteAddress  :", "PingSucceeded  : False"]
        if not port:
            return [f"ComputerName           : {host}", f"RemoteAddress          : {known[host]}", "InterfaceAlias         : Ethernet",
                    "SourceAddress          : " + str(state.get("ipv4") or "10.20.30.47"), "PingSucceeded          : True",
                    "PingReplyDetails (RTT) : 1 ms", "(Ping only proves the host answers. Add -Port to test a service.)"]
        open_ports = {"587", "443", "993"}
        ok = port in open_ports and host.startswith("mail")
        tested = state.setdefault("ports_tested", [])
        if port not in tested:
            tested.append(port)
        if "25" in tested and "587" in tested:
            mark("ports")
        out = []
        if not ok:
            out.append(f"WARNING: TCP connect to ({known[host]} : {port}) failed")
        out += [f"ComputerName     : {host}", f"RemoteAddress    : {known[host]}", f"RemotePort       : {port}",
                "InterfaceAlias   : Ethernet", "SourceAddress    : " + str(state.get("ipv4") or "10.20.30.47"),
                "PingSucceeded    : True", f"TcpTestSucceeded : {'True' if ok else 'False'}"]
        return out
    return None


WIN_LAPTOP_PORTS = _lab(
    "win-laptop-ports", "Windows CLI — Laptop & Port Diagnostics", "windows",
    "A remote laptop dies by lunch and can't send mail: read a battery report, confirm what kind of machine you are on, "
    "find the mail servers and test the SMTP ports.",
    [
        {"id": "vm_check", "text": "systeminfo — is this bench machine physical or virtual?"},
        {"id": "battery", "text": "powercfg /batteryreport, then read the user's report in C:\\Tickets"},
        {"id": "mx", "text": "Find the mail servers for ciwt.local (nslookup -type=MX or Resolve-DnsName -Type MX)"},
        {"id": "ports", "text": "Test-NetConnection mail.ciwt.local on port 25 and on port 587"},
        {"id": "q_battery", "text": "Checkpoint: battery decision"},
        {"id": "q_port", "text": "Checkpoint: read the port test"},
    ],
    "INC-31022 (LT-0442, sales): \"The battery dies by lunch, and Outlook can't send — it says it can't reach the server.\" "
    "You are on the help-desk bench machine. The user's battery report is attached in C:\\Tickets. Aliases work (tnc, gc, cat).",
    "Evidence for both faults: a worn, possibly swelling battery to replace safely, and SMTP 25 blocked while submission port 587 works.",
    _win(shell="ps"),
    course_objectives=["IT-4.1", "IT-5.1", "IT-5.2", "IT-6.1"], minutes=25, pre=_wlp_pre,
    hints=["systeminfo", "powercfg /batteryreport", "type C:\\Tickets\\battery-report-LT-0442.txt", "nslookup -type=MX ciwt.local",
           "Test-NetConnection mail.ciwt.local -Port 25", "Test-NetConnection mail.ciwt.local -Port 587"],
    obj_hints={
        "vm_check": ["systeminfo shows the System Model and whether a hypervisor is running.", "systeminfo"],
        "battery": ["powercfg makes the battery report on a laptop; on this VM, read the one attached to the ticket.",
                    "powercfg /batteryreport  then  type C:\\Tickets\\battery-report-LT-0442.txt"],
        "mx": ["Mail servers are published as MX records, not A records.", "nslookup -type=MX ciwt.local"],
        "ports": ["Ping proves the host; -Port proves the service. Test SMTP (25) and submission (587).",
                  "Test-NetConnection mail.ciwt.local -Port 25   then   -Port 587"],
    },
    palette=["systeminfo", "powercfg /batteryreport", "dir C:\\Tickets", "type ", "nslookup -type=MX ", "Test-NetConnection ", "-Port ", "cls"],
    steps=[
        _choice("q_battery", "q_battery", "The report shows design capacity 54,000 mWh, full charge capacity 30,240 mWh, 812 cycles, and the user "
                "says the touchpad feels raised. What do you do?",
                ["Recalibrate the battery and close the ticket", "Order a replacement battery; treat it as possibly swollen: power off, "
                 "don't charge or press it, remove per the service manual and recycle it properly", "Tell the user to keep it plugged in",
                 "Puncture-test the cell to confirm swelling"], 1,
                {0: "56% of design capacity after 812 cycles is wear, not calibration — and a raised touchpad suggests swelling.",
                 2: "A swelling lithium cell is a safety risk; keeping it on charge makes it worse.",
                 3: "Never puncture or press a lithium cell."},
                right="Correct: about 56% health plus a raised touchpad — replace it and handle it as a swollen battery.", title="Checkpoint"),
        _choice("q_port", "q_port", "mail.ciwt.local: PingSucceeded True; port 25 TcpTestSucceeded False; port 587 True. What does that tell you?",
                ["The mail server is down", "DNS is broken", "The host is up; port 25 is blocked or not offered to clients — "
                 "configure the client for submission on 587 (STARTTLS)", "The laptop has no IP address"], 2,
                {0: "Ping and port 587 both answer — the server is up.", 1: "The name resolved to 10.20.40.25, so DNS works.",
                 3: "The laptop reached the server on 587, so it has a working address."},
                right="Correct: the host answers; 25 is blocked for clients, 587 is the submission port to use.", title="Checkpoint"),
    ],
    solution={"commands": ["systeminfo", "powercfg /batteryreport", "type C:\\Tickets\\battery-report-LT-0442.txt",
                           "nslookup -type=MX ciwt.local", "Test-NetConnection mail.ciwt.local -Port 25",
                           "Test-NetConnection mail.ciwt.local -Port 587"],
              "answers": {"q_battery": 1, "q_port": 2}},
)



# ────────────────────────────────────────────────────────────── win-wifi-survey (ITSUP 5.4: a laptop WITH a Wi-Fi adapter)

_NETS = [("CIWT-Staff", "WPA3-Personal", "CCMP", [("a4:2b:b0:11:20:01", 34, "802.11ax", 1, "2.4 GHz"), ("a4:2b:b0:11:20:05", 86, "802.11ax", 44, "5 GHz")]),
         ("CIWT-Guest", "WPA2-Personal", "CCMP", [("a4:2b:b0:11:21:01", 31, "802.11ax", 1, "2.4 GHz")]),
         ("HP-Print-3F-LaserJet", "Open", "None", [("f0:92:1c:3f:00:aa", 70, "802.11n", 6, "2.4 GHz")]),
         ("NETGEAR-3F2A", "WPA2-Personal", "CCMP", [("9c:3d:cf:2a:3f:10", 64, "802.11ac", 1, "2.4 GHz")])]


def _wifi_pre(state, done, cmd):
    cl = re.sub(r"\s+", " ", (cmd or "").strip().lower())

    def mark(o):
        if o not in done:
            done.append(o)
    band5 = state.get("band") == "5"
    if cl in ("netsh wlan show interfaces", "netsh wlan show interface", "netsh wlan sh int"):
        mark("show_if")
        ch, sig, band, bssid = (44, 86, "5 GHz", "a4:2b:b0:11:20:05") if band5 else (1, 34, "2.4 GHz", "a4:2b:b0:11:20:01")
        if band5:
            mark("verify")
        return ["There is 1 interface on the system:", "", "    Name                   : Wi-Fi", "    Description            : Intel(R) Wi-Fi 6E AX211 160MHz",
                "    State                  : connected", "    SSID                   : CIWT-Staff", f"    BSSID                  : {bssid}",
                "    Network type           : Infrastructure", "    Radio type             : 802.11ax", "    Authentication         : WPA3-Personal",
                f"    Band                   : {band}", f"    Channel                : {ch}", f"    Receive rate (Mbps)    : {'960' if band5 else '28.9'}",
                f"    Signal                 : {sig}%", "    Profile                : CIWT-Staff"]
    if cl.startswith("netsh wlan show networks") or cl.startswith("netsh wlan sh net"):
        bssid_mode = "bssid" in cl
        if bssid_mode:
            mark("survey")
        out = [f"Interface name : Wi-Fi", f"There are {len(_NETS)} networks currently visible.", ""]
        for i, (ssid, auth, enc, aps) in enumerate(_NETS, 1):
            out += [f"SSID {i} : {ssid}", "    Network type            : Infrastructure", f"    Authentication          : {auth}",
                    f"    Encryption              : {enc}"]
            if bssid_mode:
                for j, (b, sig, radio, ch, band) in enumerate(aps, 1):
                    out += [f"    BSSID {j}                 : {b}", f"         Signal             : {sig}%", f"         Radio type         : {radio}",
                            f"         Band               : {band}", f"         Channel            : {ch}"]
            out.append("")
        if not bssid_mode:
            out.append("(Add mode=bssid to see each access point's signal, band and channel.)")
        return out
    if cl in ("netsh wlan show profiles", "netsh wlan show profile"):
        mark("profiles")
        return ["Profiles on interface Wi-Fi:", "", "User profiles", "-------------", "    All User Profile     : CIWT-Staff",
                "    All User Profile     : CIWT-Guest", "    All User Profile     : Starbucks WiFi"]
    m = re.match(r'^netsh wlan show profile (?:name=)?"?([^"]+?)"?(?: key=clear)?$', cl)
    if m and m.group(1).strip() == "ciwt-staff":
        mark("profiles")
        return ["Profile CIWT-Staff on interface Wi-Fi:", "    Connection mode        : Connect automatically", "    Authentication         : WPA3-Personal",
                "    Cipher                 : CCMP", "    Security key           : Present", "    Key Content            : (hidden by policy on this training laptop)"]
    if cl.startswith("netsh wlan connect") or cl.startswith("netsh wlan disconnect"):
        if "disconnect" in cl:
            return ["Disconnection request was completed successfully for interface \"Wi-Fi\"."]
        if "ciwt-staff" in cl:
            state["band"] = "5"
            mark("reconnect")
            return ["Connection request was completed successfully.",
                    "(Windows chose the strongest BSSID for the profile: the 5 GHz radio on channel 44.)"]
        return ["There is no profile \"%s\" assigned to the specified interface." % cmd.split("name=")[-1].strip('" ')]
    return None


WIN_WIFI_SURVEY = _lab(
    "win-wifi-survey", "Windows CLI — Wi-Fi Site Survey", "windows",
    "A laptop WITH a Wi-Fi adapter (works on any bench, VM or phone): read the interface, survey the access points, "
    "reconnect to the better band and verify.",
    [
        {"id": "show_if", "text": "netsh wlan show interfaces — read signal, band and channel"},
        {"id": "survey", "text": "netsh wlan show networks mode=bssid — survey every access point"},
        {"id": "profiles", "text": "netsh wlan show profiles — confirm the saved CIWT-Staff profile"},
        {"id": "reconnect", "text": "Reconnect to CIWT-Staff (netsh wlan connect name=CIWT-Staff)"},
        {"id": "verify", "text": "Verify with show interfaces: 5 GHz, strong signal"},
        {"id": "q_wifi", "text": "Checkpoint: why was it slow?"},
    ],
    "INC-31107 (LT-0388, 3rd floor): \"Teams keeps freezing on Wi-Fi.\" The laptop is in the meeting room next to the printer. "
    "This simulated laptop has an Intel AX211 Wi-Fi adapter, so the netsh wlan commands work here even though bench VMs have none.",
    "Diagnosed a weak 2.4 GHz connection on a crowded channel 1 and moved the laptop to the 5 GHz radio of the same network.",
    _win(shell="cmd"),
    course_objectives=["IT-5.4", "NO-3.3"], minutes=20, pre=_wifi_pre,
    hints=["netsh wlan show interfaces", "netsh wlan show networks mode=bssid", "netsh wlan show profiles",
           "netsh wlan connect name=CIWT-Staff", "netsh wlan show interfaces"],
    obj_hints={
        "show_if": ["Start with the adapter's own view of the link.", "netsh wlan show interfaces"],
        "survey": ["List the networks with each access point (BSSID) to compare bands and channels.", "netsh wlan show networks mode=bssid"],
        "profiles": ["Check the laptop has the right saved network before reconnecting.", "netsh wlan show profiles"],
        "reconnect": ["Reconnecting lets Windows pick the strongest BSSID for the profile.", "netsh wlan connect name=CIWT-Staff"],
        "verify": ["Prove the fix with the same command you diagnosed with.", "netsh wlan show interfaces"],
    },
    palette=["netsh wlan show interfaces", "netsh wlan show networks mode=bssid", "netsh wlan show profiles", "netsh wlan connect name=", "cls"],
    steps=[
        _choice("q_wifi", "q_wifi", "Before the fix: CIWT-Staff at 34% on 2.4 GHz channel 1, which NETGEAR-3F2A and CIWT-Guest also use; "
                "the same SSID offered 86% on 5 GHz channel 44. Best explanation?",
                ["The WPA3 password is wrong", "The laptop held a weak 2.4 GHz link on a busy channel instead of the strong 5 GHz radio",
                 "The DHCP server is down", "The printer's open network is blocking Teams"], 1,
                {0: "It was connected and authenticated — a wrong key would not connect at all.",
                 2: "It had a working connection; the issue was link quality.",
                 3: "An open SSID on channel 6 doesn't block anything; the shared channel 1 and weak signal do."},
                right="Correct: weak signal + co-channel contention on 2.4 GHz; the 5 GHz radio was the fix.", title="Checkpoint"),
    ],
    solution={"commands": ["netsh wlan show interfaces", "netsh wlan show networks mode=bssid", "netsh wlan show profiles",
                           "netsh wlan connect name=CIWT-Staff", "netsh wlan show interfaces"], "answers": {"q_wifi": 1}},
)

# ────────────────────────────────────────────────────────────── hv-vswitch (ITSUP 6.3: Hyper-V host, simulated)

def _hv_pre(state, done, cmd):
    c = re.sub(r"\s+", " ", (cmd or "").strip())
    cl = c.lower()
    hv = state.setdefault("hv", {"switches": [{"name": "Default Switch", "type": "Internal"}],
                                 "vms": {"LAB-W11": {"state": "Running", "switch": "Default Switch", "cps": []},
                                         "LAB-SRV": {"state": "Off", "switch": "", "cps": []}}})

    def mark(o):
        if o not in done:
            done.append(o)

    def arg(name):
        m = re.search(r"-" + name + r"\s+(\"[^\"]+\"|'[^']+'|\S+)", c, re.I)
        return m.group(1).strip("\"'") if m else None
    if cl in ("get-vm",):
        mark("get_vm")
        out = ["Name    State   CPUUsage(%) MemoryAssigned(M) Uptime   Status             Version", "----    -----   ----------- ----------------- ------   ------             -------"]
        for n, v in hv["vms"].items():
            out.append(f"{n:<8}{v['state']:<8}{'3' if v['state'] == 'Running' else '0':<12}{'4096' if v['state'] == 'Running' else '0':<18}"
                       f"{'02:14:07' if v['state'] == 'Running' else '00:00:00':<9}Operating normally 11.0")
        return out
    if cl.startswith("get-vmswitch"):
        mark("get_switch")
        out = ["Name           SwitchType NetAdapterInterfaceDescription", "----           ---------- ------------------------------"]
        for sw in hv["switches"]:
            out.append(f"{sw['name']:<15}{sw['type']:<11}{'Intel(R) Ethernet I219-LM' if sw['type'] == 'External' else ''}")
        return out
    if cl.startswith("new-vmswitch"):
        name, typ = arg("name"), (arg("switchtype") or "")
        if not name:
            return ["New-VMSwitch : Cannot validate argument on parameter 'Name'. Example: New-VMSwitch -Name Lab-Private -SwitchType Private"]
        if any(sw["name"].lower() == name.lower() for sw in hv["switches"]):
            return [f"New-VMSwitch : A virtual switch named '{name}' already exists."]
        if arg("netadaptername"):
            typ = "External"
        if typ.lower() not in ("private", "internal", "external"):
            return ["New-VMSwitch : -SwitchType must be Private, Internal or External (External needs -NetAdapterName instead)."]
        hv["switches"].append({"name": name, "type": typ.capitalize()})
        state["_hv_last_switch"] = name
        if typ.lower() == "private":
            mark("new_switch")
            note = []
        else:
            note = [f"(Created a {typ.capitalize()} switch. The ticket needs an isolated lab network: VMs only, no host or LAN access — that is Private.)"]
        return [f"Name           SwitchType", "----           ----------", f"{name:<15}{typ.capitalize()}"] + note
    if cl.startswith("remove-vmswitch"):
        name = arg("name") or (c.split()[1] if len(c.split()) > 1 else "")
        hv["switches"] = [sw for sw in hv["switches"] if sw["name"].lower() != name.strip("\"'").lower() or sw["name"] == "Default Switch"]
        return [f"(Removed virtual switch {name})"]
    if cl.startswith("connect-vmnetworkadapter"):
        vm, sw = arg("vmname"), arg("switchname")
        if vm not in hv["vms"]:
            return [f"Connect-VMNetworkAdapter : Hyper-V was unable to find a virtual machine with name \"{vm}\".  (Get-VM lists them.)"]
        swo = next((x for x in hv["switches"] if x["name"].lower() == (sw or "").lower()), None)
        if not swo:
            return [f"Connect-VMNetworkAdapter : Virtual switch \"{sw}\" not found.  (Get-VMSwitch lists them.)"]
        hv["vms"][vm]["switch"] = swo["name"]
        if swo["type"] == "Private" and hv["vms"]["LAB-W11"]["switch"] == hv["vms"]["LAB-SRV"]["switch"] == swo["name"]:
            mark("connect")
        return []
    if cl.startswith("get-vmnetworkadapter"):
        out = ["VMName  Name             SwitchName     MacAddress   Status", "------  ----             ----------     ----------   ------"]
        for n, v in hv["vms"].items():
            out.append(f"{n:<8}Network Adapter  {v['switch'] or '(not connected)':<15}00155D0A1E{47 if n == 'LAB-W11' else 48}   {'{Ok}' if v['state'] == 'Running' else ''}")
        return out
    if cl.startswith("start-vm"):
        vm = arg("name") or (c.split()[1] if len(c.split()) > 1 else "")
        if vm in hv["vms"]:
            hv["vms"][vm]["state"] = "Running"
            return []
        return [f"Start-VM : Hyper-V was unable to find a virtual machine with name \"{vm}\"."]
    if cl.startswith("checkpoint-vm"):
        vm, snap = arg("name") or arg("vmname"), arg("snapshotname")
        if vm not in hv["vms"]:
            return [f"Checkpoint-VM : Hyper-V was unable to find a virtual machine with name \"{vm}\"."]
        snap = snap or f"{vm} - ({len(hv['vms'][vm]['cps']) + 1})"
        hv["vms"][vm]["cps"].append(snap)
        if vm == "LAB-W11":
            mark("checkpoint")
        return []
    if cl.startswith("get-vmcheckpoint") or cl.startswith("get-vmsnapshot"):
        vm = arg("vmname") or arg("name") or "LAB-W11"
        cps = hv["vms"].get(vm, {}).get("cps", [])
        if cps and vm == "LAB-W11":
            mark("list_cp")
        if not cps:
            return [f"(No checkpoints for {vm}.)"]
        return ["VMName  Name                 SnapshotType CreationTime", "------  ----                 ------------ ------------"] + \
               [f"{vm:<8}{n:<21}Standard     10/17/2026 4:1{i} PM" for i, n in enumerate(cps)]
    if cl.startswith("restore-vmcheckpoint") or cl.startswith("restore-vmsnapshot"):
        vm, name = arg("vmname"), arg("name")
        if vm in hv["vms"] and name in hv["vms"][vm]["cps"]:
            state["restored"] = True
            mark("restore")
            return ["Confirm", f"Are you sure you want to apply checkpoint \"{name}\"? [Y] Yes: Y", f"(LAB-W11 returned to \"{name}\". Changes since then are discarded.)"]
        return ["Restore-VMCheckpoint : the checkpoint was not found. Example: Restore-VMCheckpoint -VMName LAB-W11 -Name pre-update"]
    return None


HV_VSWITCH = _lab(
    "hv-vswitch", "Hyper-V Switch & Checkpoints", "windows",
    "On a simulated Hyper-V host: build a Private switch for a lab network, connect two VMs, checkpoint before an update and roll back.",
    [
        {"id": "get_vm", "text": "Get-VM — list the virtual machines"},
        {"id": "get_switch", "text": "Get-VMSwitch — list the existing virtual switches"},
        {"id": "new_switch", "text": "Create an isolated switch: New-VMSwitch -Name Lab-Private -SwitchType Private"},
        {"id": "connect", "text": "Connect LAB-W11 and LAB-SRV to Lab-Private (Connect-VMNetworkAdapter)"},
        {"id": "checkpoint", "text": "Checkpoint LAB-W11 before the update (Checkpoint-VM -Name LAB-W11 -SnapshotName pre-update)"},
        {"id": "list_cp", "text": "Get-VMCheckpoint -VMName LAB-W11 — confirm it exists"},
        {"id": "restore", "text": "The update broke the VM: Restore-VMCheckpoint -VMName LAB-W11 -Name pre-update"},
        {"id": "q_switch", "text": "Checkpoint: switch types"},
    ],
    "CHG-2207 on HV-LAB01 (a Hyper-V host; you are in an elevated PowerShell): the trainers need LAB-W11 and LAB-SRV on a network "
    "that can't reach the host or the office LAN, and a safe rollback point before a risky update.",
    "Isolated lab network built, both VMs attached, update rolled back from a checkpoint — no host or LAN exposure.",
    _win(shell="ps", hostname="HV-LAB01"),
    course_objectives=["IT-6.1", "IT-6.3"], minutes=25, pre=_hv_pre,
    hints=["Get-VM", "Get-VMSwitch", "New-VMSwitch -Name Lab-Private -SwitchType Private",
           "Connect-VMNetworkAdapter -VMName LAB-W11 -SwitchName Lab-Private", "Connect-VMNetworkAdapter -VMName LAB-SRV -SwitchName Lab-Private",
           "Checkpoint-VM -Name LAB-W11 -SnapshotName pre-update", "Get-VMCheckpoint -VMName LAB-W11",
           "Restore-VMCheckpoint -VMName LAB-W11 -Name pre-update"],
    obj_hints={
        "get_vm": ["Inventory first: which VMs are on this host?", "Get-VM"],
        "get_switch": ["Which virtual switches exist already, and of what type?", "Get-VMSwitch"],
        "new_switch": ["Private = VMs talk only to each other; Internal adds the host; External adds the physical LAN.",
                       "New-VMSwitch -Name Lab-Private -SwitchType Private"],
        "connect": ["Each VM's network adapter is attached to one switch.",
                    "Connect-VMNetworkAdapter -VMName LAB-W11 -SwitchName Lab-Private  (then the same for LAB-SRV)"],
        "checkpoint": ["Take the checkpoint BEFORE the change.", "Checkpoint-VM -Name LAB-W11 -SnapshotName pre-update"],
        "list_cp": ["Prove the rollback point exists.", "Get-VMCheckpoint -VMName LAB-W11"],
        "restore": ["Apply the checkpoint to roll back.", "Restore-VMCheckpoint -VMName LAB-W11 -Name pre-update"],
    },
    palette=["Get-VM", "Get-VMSwitch", "New-VMSwitch -Name ", "-SwitchType Private", "Connect-VMNetworkAdapter -VMName ", "-SwitchName ",
             "Checkpoint-VM -Name ", "Get-VMCheckpoint -VMName ", "Restore-VMCheckpoint -VMName ", "Get-VMNetworkAdapter *"],
    steps=[
        _choice("q_switch", "q_switch", "A trainer now wants the host itself to reach the lab VMs, but still no office LAN access. Which switch type?",
                ["Private", "Internal", "External", "Default Switch with NAT disabled"], 1,
                {0: "Private excludes the host.", 2: "External bridges to the physical LAN.", 3: "Default Switch is an Internal switch with NAT to the LAN — it gives LAN/internet access."},
                right="Correct: Internal = VMs + host, no physical LAN.", title="Checkpoint"),
    ],
    solution={"commands": ["Get-VM", "Get-VMSwitch", "New-VMSwitch -Name Lab-Private -SwitchType Private",
                           "Connect-VMNetworkAdapter -VMName LAB-W11 -SwitchName Lab-Private",
                           "Connect-VMNetworkAdapter -VMName LAB-SRV -SwitchName Lab-Private",
                           "Checkpoint-VM -Name LAB-W11 -SnapshotName pre-update", "Get-VMCheckpoint -VMName LAB-W11",
                           "Restore-VMCheckpoint -VMName LAB-W11 -Name pre-update"],
              "answers": {"q_switch": 1}},
)


NEW_LABS = [NET_SUBNET, HW_CABLES, HW_PC_BUILD, TICKET_METHOD, WIN_NET_CLI, LINUX_SHELL, PRINT_TROUBLE, RTR_VLAN_ACL, SW_VLAN_MULTI,
            WIFI_SECURE, SEC_MALWARE, OPS_BACKUP, VIRT_VM, MOB_MDM, WIN_AD_USERS,
            WIN_LAPTOP_PORTS, WIN_WIFI_SURVEY, HV_VSWITCH]

# Real-environment labs (a genuine Linux VM in the browser, v86) — see labs_vm.py
from labs_vm import VM_LABS as _VM_LABS  # noqa: E402
NEW_LABS += _VM_LABS

for _l in NEW_LABS:
    if _l["kind"] == "win11gui":
        _l["initial_state"] = _win(gui=gui_state(default_ad() if _l.get("gui_ad") else None))
    if not _l.get("hints") and _l.get("obj_hints"):
        _l["hints"] = [h[0] for h in _l["obj_hints"].values()]

NEW_CHAPTER_LABS = {
    ("ITSUP", 2): ["hw-pc-build"],
    ("ITSUP", 3): ["hw-cables", "hw-pc-build", "linux-vm-disk"],
    ("ITSUP", 4): ["print-trouble", "mob-mdm", "win-laptop-ports"],
    ("ITSUP", 5): ["net-subnet", "win-net-cli", "wifi-secure", "win-laptop-ports", "win-wifi-survey", "linux-vm-netclient", "linux-vm-routing", "linux-vm-dns", "linux-vm-web", "linux-vm-ipv6"],
    ("ITSUP", 6): ["virt-vm", "win-laptop-ports", "hv-vswitch"],
    ("ITSUP", 7): ["ticket-method", "linux-vm-method"],
    ("ITSUP", 8): ["win-ad-users"],
    ("ITSUP", 9): ["linux-vm-shell", "linux-shell", "linux-vm-perms", "linux-vm-services", "linux-vm-logs", "linux-vm-cron", "linux-vm-users", "linux-vm-packages", "linux-vm-disk", "linux-vm-ssh", "linux-vm-script", "linux-vm-perf", "linux-vm-web"],
    ("ITSUP", 10): ["sec-malware", "win-ad-users", "linux-vm-users", "linux-vm-firewall", "linux-vm-logs", "linux-vm-packages", "linux-vm-incident"],
    ("ITSUP", 11): ["linux-vm-perf"],
    ("ITSUP", 12): ["ops-backup", "linux-vm-cron", "linux-vm-script", "linux-vm-restore", "linux-vm-web"],
    ("ITSUP", 13): ["win-net-cli", "print-trouble", "linux-vm-netclient", "linux-vm-dns"],
    ("NETOPS", 1): ["net-subnet", "linux-vm-nettrouble", "linux-vm-web", "linux-vm-ipv6"],
    ("NETOPS", 2): ["sw-vlan-multi", "hw-cables"],
    ("NETOPS", 3): ["wifi-secure", "win-wifi-survey", "linux-vm-nat", "linux-vm-ipv6"],
    ("NETOPS", 4): ["win-net-cli", "rtr-vlan-acl", "linux-vm-netclient", "linux-vm-dns", "linux-vm-firewall", "linux-vm-nettrouble", "linux-vm-nat"],
    ("NETOPS", 5): ["rtr-vlan-acl", "wifi-secure", "linux-vm-services", "linux-vm-firewall", "linux-vm-ssh", "linux-vm-logs"],
    ("NETOPS", 6): ["ticket-method", "linux-vm-nettrouble", "linux-vm-nat"],
    ("NETOPS", 9): ["sw-vlan-multi", "rtr-vlan-acl", "linux-vm-routing"],
}

# CLIENT chapters 1-6 correspond to ITSUP 8-13
for (_c, _ch), _ids in list(NEW_CHAPTER_LABS.items()):
    if _c == "ITSUP" and 8 <= _ch <= 13:
        NEW_CHAPTER_LABS.setdefault(("CLIENT", _ch - 7), [])
        NEW_CHAPTER_LABS[("CLIENT", _ch - 7)] += [i for i in _ids if i not in NEW_CHAPTER_LABS[("CLIENT", _ch - 7)]]

NEW_LAB_ALIGN = {l["id"]: l["blurb"] for l in NEW_LABS}
