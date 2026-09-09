"""CIWT IT A-school block outline — original schoolhouse map.
Public IT rating tasks only. Proprietary CIWT map — not official NAVEDTRA courseware.
~24 instructional weeks compressed into blocks a convening can run.
"""

BLOCKS = [
    {
        "id": "b1",
        "week": "1–2",
        "hours": 64,
        "title": "Block 1 — Workplace, tickets, and safety",
        "goal": "A Sailor can take a trouble call, write a ticket, and work on a PC without hurting the gear or the person.",
        "eos": [
            {"id": "b1-e1", "text": "List ESD and power-safety steps before opening a case", "lab": None, "check": "Name the order: power off, wall unplug, wait, strap, open."},
            {"id": "b1-e2", "text": "Classify a contact and write a ticket another watch can use", "lab": "ticket-intake", "check": "Finish Lab ticket-intake with classify, impact, escalate, note, submit."},
            {"id": "b1-e3", "text": "Explain change awareness: what you touch, what you document", "lab": None, "check": "Say whether adding DNS is a change or a repair."},
        ],
    },
    {
        "id": "b2",
        "week": "3–5",
        "hours": 96,
        "title": "Block 2 — Hardware and storage",
        "goal": "Identify the box, the disks, and the adapters before replacing parts.",
        "eos": [
            {"id": "b2-e1", "text": "Identify form factor, socket, memory, storage, and POST from a bench card", "lab": "hw-board", "check": "Submit Lab hw-board with the card values."},
            {"id": "b2-e2", "text": "Read Windows identity: name, edition, build", "lab": "gui-about", "check": None},
            {"id": "b2-e3", "text": "Inventory with hostname, whoami, systeminfo", "lab": "w11-inventory", "check": None},
            {"id": "b2-e4", "text": "List disks before any wipe or image", "lab": "w11-disk", "check": None},
        ],
    },
    {
        "id": "b3",
        "week": "6–8",
        "hours": 96,
        "title": "Block 3 — Windows 11 client administration",
        "goal": "Use Settings and CLI as two views of the same PC.",
        "eos": [
            {"id": "b3-e1", "text": "Open Windows Update and read patch state", "lab": "gui-update", "check": None},
            {"id": "b3-e2", "text": "Read the signed-in account", "lab": "gui-accounts", "check": None},
            {"id": "b3-e3", "text": "Confirm DHCP Client, DNS Client, Defender in Services", "lab": "gui-services", "check": None},
            {"id": "b3-e4", "text": "Same services from PowerShell", "lab": "w11-services", "check": None},
            {"id": "b3-e5", "text": "List processes before you reboot", "lab": "w11-processes", "check": None},
            {"id": "b3-e6", "text": "Read firewall profile state", "lab": "w11-firewall", "check": None},
        ],
    },
    {
        "id": "b4",
        "week": "9–12",
        "hours": 128,
        "title": "Block 4 — Client networking (DHCP, DNS, isolation)",
        "goal": "Prove address, name, and gateway as separate fault domains.",
        "eos": [
            {"id": "b4-e1", "text": "Collect ipconfig /all as ticket evidence", "lab": "win-ipconfig", "check": None},
            {"id": "b4-e2", "text": "Read the same facts in Settings → Ethernet", "lab": "gui-ethernet", "check": None},
            {"id": "b4-e3", "text": "Read the same facts with netsh", "lab": "w11-netsh", "check": None},
            {"id": "b4-e4", "text": "Isolate a name-resolution failure", "lab": "win-dns-break", "check": None},
            {"id": "b4-e5", "text": "Release and renew a lease", "lab": "win-dhcp-renew", "check": None},
            {"id": "b4-e6", "text": "Recycle the adapter from ncpa.cpl", "lab": "gui-renew", "check": None},
            {"id": "b4-e7", "text": "Run a full client triage ticket", "lab": "win-full-triage", "check": None},
            {"id": "b4-e8", "text": "Read WLAN interface state", "lab": "w11-wlan", "check": None},
            {"id": "b4-e9", "text": "Read the ARP cache", "lab": "win-arp", "check": None},
        ],
    },
    {
        "id": "b5",
        "week": "13–16",
        "hours": 128,
        "title": "Block 5 — Switching: VLANs, trunks, port security",
        "goal": "Put a user in a VLAN, trunk the uplink, lock the access port, save the config.",
        "eos": [
            {"id": "b5-e1", "text": "Create a VLAN and an access port", "lab": "sw-vlan-access", "check": None},
            {"id": "b5-e2", "text": "Build a trunk uplink", "lab": "sw-trunk-basics", "check": None},
            {"id": "b5-e3", "text": "VLAN plus trunk in one pass", "lab": "sw-vlan-and-trunk", "check": None},
            {"id": "b5-e4", "text": "Enable port-security on the access port", "lab": "sw-port-security", "check": None},
            {"id": "b5-e5", "text": "Set hostname and write memory", "lab": "sw-hostname-write", "check": None},
            {"id": "b5-e6", "text": "Explain DTP risk in one sentence", "lab": None, "check": "Why do we set mode trunk instead of hoping DTP gets it right?"},
            {"id": "b5-e7", "text": "Set a login banner on the closet switch", "lab": "sw-banner", "check": None},
        ],
    },
    {
        "id": "b6",
        "week": "17–20",
        "hours": 128,
        "title": "Block 6 — Routing: gateways and default route",
        "goal": "Bring up LAN interfaces, prove connected routes, add a default route, save.",
        "eos": [
            {"id": "b6-e1", "text": "Address a LAN interface and ping the host", "lab": "rtr-gateway", "check": None},
            {"id": "b6-e2", "text": "Bring up two LANs", "lab": "rtr-two-interfaces", "check": None},
            {"id": "b6-e3", "text": "Edge capstone: routes and both pings", "lab": "rtr-edge-complete", "check": None},
            {"id": "b6-e4", "text": "Add a default route from global config", "lab": "rtr-default-route", "check": None},
            {"id": "b6-e5", "text": "Hostname and write memory on the router", "lab": "rtr-hostname-write", "check": None},
        ],
    },
    {
        "id": "b7",
        "week": "21–22",
        "hours": 64,
        "title": "Block 7 — Security habits on the endpoint",
        "goal": "Accounts, Defender, firewall — look before you disable anything.",
        "eos": [
            {"id": "b7-e1", "text": "Read who is signed in before a password reset", "lab": "gui-accounts", "check": None},
            {"id": "b7-e2", "text": "Confirm Defender service is running", "lab": "gui-services", "check": None},
            {"id": "b7-e3", "text": "Read firewall profiles", "lab": "w11-firewall", "check": None},
            {"id": "b7-e4", "text": "State when you escalate vs local fix", "lab": None, "check": "Give one ticket you would escalate and why."},
        ],
    },
    {
        "id": "b8",
        "week": "23–24",
        "hours": 64,
        "title": "Block 8 — Capstone convening",
        "goal": "Run a full ticket from client through VLAN to gateway.",
        "eos": [
            {"id": "b8-e1", "text": "Client triage under time", "lab": "win-full-triage", "check": None},
            {"id": "b8-e2", "text": "Switch path under time", "lab": "sw-vlan-and-trunk", "check": None},
            {"id": "b8-e3", "text": "Router path under time", "lab": "rtr-edge-complete", "check": None},
            {"id": "b8-e4", "text": "Write the closing ticket", "lab": None, "check": "Symptom, tests, root cause, fix, verify ping and user workflow."},
        ],
    },
]


CSCHOOL_COMMS = [
    {
        "id": "cc1",
        "week": "C-Comms 1–3",
        "hours": 120,
        "title": "C-school — Communications path",
        "goal": "After A-school, run the edge: VLANs, trunks, dual LAN, default route, and a clean ticket.",
        "eos": [
            {"id": "cc1-e1", "text": "Rebuild VLAN + trunk without notes", "lab": "sw-vlan-and-trunk", "check": None},
            {"id": "cc1-e2", "text": "Port-security on the user drop", "lab": "sw-port-security", "check": None},
            {"id": "cc1-e3", "text": "Two LAN interfaces and both pings", "lab": "rtr-two-interfaces", "check": None},
            {"id": "cc1-e4", "text": "Default route from global config (exit the interface first)", "lab": "rtr-default-route", "check": None},
            {"id": "cc1-e5", "text": "Save the router config", "lab": "rtr-hostname-write", "check": None},
            {"id": "cc1-e6", "text": "Write the comms ticket: circuit up, users pass", "lab": None, "check": "One paragraph: tests, root cause, verify."},
            {"id": "cc1-e7", "text": "Read the MAC address table", "lab": "sw-mac-table", "check": None},
            {"id": "cc1-e8", "text": "Describe the user LAN interface", "lab": "rtr-describe", "check": None},
            {"id": "cc1-e9", "text": "show interfaces status on the switch", "lab": "sw-int-status", "check": None},
            {"id": "cc1-e10", "text": "Traceroute from the router to the LAN host", "lab": "rtr-trace", "check": None},
        ],
    },
    {
        "id": "cc2",
        "week": "C-Comms 4–5",
        "hours": 80,
        "title": "C-school — Communications path · identify the box",
        "goal": "Version, labels, MAC table, interface status — before you change a live edge.",
        "eos": [
            {"id": "cc2-e1", "text": "show version on the closet switch", "lab": "sw-show-ver", "check": None},
            {"id": "cc2-e2", "text": "Describe the user drop", "lab": "sw-describe", "check": None},
            {"id": "cc2-e3", "text": "Interface status board", "lab": "sw-int-status", "check": None},
            {"id": "cc2-e4", "text": "Login banner", "lab": "sw-banner", "check": None},
        ],
    },
]

CSCHOOL_SYS = [
    {
        "id": "cs1",
        "week": "C-Sys 1–4",
        "hours": 160,
        "title": "C-school — Systems administrator path",
        "goal": "Treat the Windows 11 endpoint like a managed client: identity, services, firewall, processes, isolation.",
        "eos": [
            {"id": "cs1-e1", "text": "Inventory the endpoint", "lab": "w11-inventory", "check": None},
            {"id": "cs1-e2", "text": "Services: DHCP, DNS, Defender", "lab": "w11-services", "check": None},
            {"id": "cs1-e3", "text": "Firewall profiles", "lab": "w11-firewall", "check": None},
            {"id": "cs1-e4", "text": "Process list before reboot", "lab": "w11-processes", "check": None},
            {"id": "cs1-e5", "text": "Full client triage", "lab": "win-full-triage", "check": None},
            {"id": "cs1-e6", "text": "What you do not change on a shipboard server without a change ticket", "lab": None, "check": "Name two changes that need change control first."},
            {"id": "cs1-e7", "text": "WLAN interface report", "lab": "w11-wlan", "check": None},
            {"id": "cs1-e8", "text": "Print the IPv4 route table", "lab": "win-route", "check": None},
            {"id": "cs1-e9", "text": "Read the adapter MAC", "lab": "win-getmac", "check": None},
            {"id": "cs1-e10", "text": "List active connections", "lab": "win-netstat", "check": None},
            {"id": "cs1-e11", "text": "Print the hostname", "lab": "win-hostname", "check": None},
            {"id": "cs1-e12", "text": "Loopback ping", "lab": "win-ping-loop", "check": None},
            {"id": "cs1-e13", "text": "Working nslookup", "lab": "win-nslookup-ok", "check": None},
            {"id": "cs1-e14", "text": "Flush DNS cache", "lab": "win-flushdns", "check": None},
        ],
    },
]


def all_eos(blocks=None):
    rows = []
    for b in (blocks if blocks is not None else BLOCKS):
        for e in b["eos"]:
            rows.append({**e, "block": b})
    return rows


def outline_stats(blocks=None):
    use = blocks if blocks is not None else BLOCKS
    eos = all_eos(use)
    return {
        "blocks": len(use),
        "hours": sum(b["hours"] for b in use),
        "eos": len(eos),
        "with_lab": sum(1 for e in eos if e.get("lab")),
        "checklist_only": sum(1 for e in eos if not e.get("lab")),
    }
