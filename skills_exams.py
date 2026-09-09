"""True skills exams: timed lab stations (CLI + GUI), not multiple choice."""


def station(lab_id, area):
    return {"lab_id": lab_id, "area": area, "kind": "lab"}


def practical(stations):
    return {"kind": "practical", "stations": stations}


ITSUP_MIDTERM = practical([
    station("ticket-intake", "Tickets & safety"),
    station("hw-board", "Hardware"),
    station("win-ipconfig", "Client network"),
    station("gui-about", "Windows GUI"),
])

ITSUP_FINAL = practical([
    station("ticket-intake", "Tickets & safety"),
    station("hw-board", "Hardware"),
    station("win-full-triage", "Client network"),
    station("win-dns-break", "Name resolution"),
    station("gui-ethernet", "Windows GUI"),
    station("gui-accounts", "Windows GUI"),
])

NETOPS_MIDTERM = practical([
    station("sw-vlan-access", "Switching"),
    station("rtr-gateway", "Routing"),
    station("win-ipconfig", "Client network"),
])

NETOPS_FINAL = practical([
    station("sw-vlan-and-trunk", "Switching"),
    station("rtr-edge-complete", "Routing"),
    station("win-dns-break", "Services"),
    station("win-full-triage", "Operations"),
])

CLIENT_MIDTERM = practical([
    station("gui-about", "Windows client"),
    station("gui-accounts", "Windows client"),
    station("w11-inventory", "Windows client"),
    station("ticket-intake", "Tickets & safety"),
])

CLIENT_FINAL = practical([
    station("win-full-triage", "Software / network"),
    station("gui-update", "Windows client"),
    station("gui-services", "Windows client"),
    station("ticket-intake", "Tickets & safety"),
    station("gui-accounts", "Security"),
])


SPECS = {
    "ITSUP": [
        ("Skills Midterm — IT Support",
         "Hands-on: ticket intake, board ID, ipconfig, Settings About. Pass 80%. 40 minutes.",
         10, ITSUP_MIDTERM, 40, 80),
        ("Skills Final — IT Support",
         "Hands-on: intake, board, full triage, DNS break, Ethernet GUI, Accounts GUI. Pass 80%. 60 minutes.",
         20, ITSUP_FINAL, 60, 80),
    ],
    "NETOPS": [
        ("Skills Midterm — Network Operations",
         "Hands-on: VLAN access port, router gateway, client ipconfig. Pass 80%. 30 minutes.",
         10, NETOPS_MIDTERM, 30, 80),
        ("Skills Final — Network Operations",
         "Hands-on: VLAN+trunk capstone, router edge, DNS break, full triage. Pass 80%. 45 minutes.",
         20, NETOPS_FINAL, 45, 80),
    ],
    "CLIENT": [
        ("Skills Midterm — Client Systems",
         "Hands-on: About, Accounts, inventory, ticket. Pass 80%. 30 minutes.",
         10, CLIENT_MIDTERM, 30, 80),
        ("Skills Final — Client Systems",
         "Hands-on: full triage, Update, Services, ticket, Accounts. Pass 80%. 45 minutes.",
         20, CLIENT_FINAL, 45, 80),
    ],
}


def exams_for(code):
    return SPECS.get(code) or []


def is_practical_payload(payload):
    if isinstance(payload, dict):
        return payload.get("kind") == "practical"
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0].get("kind") == "practical"
    return False


def stations_of(payload):
    if isinstance(payload, dict):
        return payload.get("stations") or []
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0].get("stations") or []
    return []
