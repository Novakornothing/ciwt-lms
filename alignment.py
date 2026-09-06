"""CIWT skill map for IT Support and Network Operations.
Original wording — proprietary schoolhouse objectives, not vendor exam text.
"""

ITSUP_DOMAINS = [
    {
        "name": "Workplace, safety, and tickets",
        "topics": "ESD, documentation, professionalism, change awareness",
        "labs": [],
        "note": "Taught in Chapter 1. Practice is checklist and ticket writing, not a CLI box.",
    },
    {
        "name": "PC hardware and firmware",
        "topics": "Motherboard, CPU, RAM, storage, PSU, ports, UEFI",
        "labs": ["w11-disk", "gui-devices", "w11-inventory"],
        "note": "Chapters 2–3. Device Manager + list disk before you image or replace parts.",
    },
    {
        "name": "Mobile and printing",
        "topics": "Laptop FRUs, mobile accounts, print path",
        "labs": ["gui-accounts"],
        "note": "Chapter 4. Print path is in curriculum; GUI Accounts covers signed-in identity.",
    },
    {
        "name": "Client networking",
        "topics": "IPv4, ports, isolation order, SOHO wireless, DHCP, DNS",
        "labs": [
            "win-ipconfig", "win-dns-break", "win-dhcp-renew", "win-full-triage",
            "w11-powershell-net", "w11-netsh", "gui-ethernet", "gui-renew",
            "win-hostname", "win-ping-loop", "win-nslookup-ok", "win-flushdns",
            "win-arp", "win-route", "win-getmac", "win-netstat", "w11-wlan",
        ],
        "note": "Chapter 5 and 13. Same facts from CLI and Settings.",
    },
    {
        "name": "OS install and Windows 11 admin",
        "topics": "Install types, baseline, repair, Update, services, firewall, processes",
        "labs": [
            "w11-inventory", "gui-about", "gui-update", "gui-services",
            "w11-services", "w11-firewall", "w11-processes",
        ],
        "note": "Chapters 8, 11, 13.",
    },
    {
        "name": "Security and operations",
        "topics": "Accounts, Defender, malware response, change control",
        "labs": ["gui-accounts", "gui-services", "w11-services"],
        "note": "Chapters 10 and 12.",
    },
]

NETOPS_DOMAINS = [
    {
        "name": "Models and addressing",
        "topics": "OSI/TCP-IP thinking, IPv4 ideas, TCP vs UDP",
        "labs": ["win-ipconfig"],
        "note": "Chapter 1. Addressing is conceptual first, then the Windows identity lab.",
    },
    {
        "name": "Switching, VLANs, trunks",
        "topics": "MAC learning, access ports, trunks, port security",
        "labs": ["sw-vlan-access", "sw-trunk-basics", "sw-vlan-and-trunk", "sw-port-security", "sw-hostname-write", "sw-mac-table", "sw-banner", "sw-int-status", "sw-show-ver", "sw-describe"],
        "note": "Chapters 2 and 9.",
    },
    {
        "name": "Routing and WAN edge",
        "topics": "Connected routes, dual interfaces, default route",
        "labs": ["rtr-gateway", "rtr-two-interfaces", "rtr-edge-complete", "rtr-default-route", "rtr-hostname-write", "rtr-describe", "rtr-trace"],
        "note": "Chapters 3 and 9.",
    },
    {
        "name": "DHCP, DNS, NAT, firewall",
        "topics": "Client lease, name resolution, edge filtering",
        "labs": ["win-dhcp-renew", "win-dns-break", "win-full-triage", "w11-firewall"],
        "note": "Chapter 4. Server-side pools stay in curriculum until a later lab track.",
    },
    {
        "name": "Operations and troubleshooting",
        "topics": "Monitoring, segmentation, ordered isolation",
        "labs": ["win-full-triage", "sw-vlan-and-trunk", "rtr-edge-complete"],
        "note": "Chapters 5–6.",
    },
]


def domains_for_course(course):
    code = (getattr(course, "code", None) or "") if course is not None else ""
    if code == "NETOPS":
        return NETOPS_DOMAINS
    return ITSUP_DOMAINS
