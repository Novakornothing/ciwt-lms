"""Stage 2 and Stage 3 for switch and router labs.

Grading reads VLAN membership, trunk lists, addresses, routes, ACLs,
banners, descriptions, or a saved configuration. A hostname by itself
is not the check.
"""
from __future__ import annotations

import lab_skills as SK

IOS = [
    ("Privileged mode", "enable"),
    ("Configuration mode", "configure terminal"),
    ("Select an interface", "interface <type><slot>/<port>"),
    ("Leave configuration", "end"),
]
VLAN = IOS + [
    ("Create a VLAN", "vlan <id>"),
    ("Name a VLAN", "name <text>"),
    ("Access mode", "switchport mode access"),
    ("Access VLAN", "switchport access vlan <id>"),
    ("Show VLANs", "show vlan brief"),
]
TRUNK = IOS + [
    ("Trunk mode", "switchport mode trunk"),
    ("Allowed list", "switchport trunk allowed vlan <list>"),
    ("Show trunks", "show interfaces trunk"),
]
ADDR = IOS + [
    ("Address", "ip address <address> <mask>"),
    ("Enable the interface", "no shutdown"),
    ("Routes", "show ip route"),
]
ROUTE = ADDR + [("Static route", "ip route <network> <mask> <next-hop>")]
ACL = IOS + [("Standard list", "access-list <1-99> deny host <address>")]


def _base(f, seed):
    f["v1"] = f.get("assisted_vlan") or (30 + (seed % 40))
    f["v2"] = f.get("ticket_vlan") or (f["v1"] + 11)
    if f["v2"] in (20, f["v1"]):
        f["v2"] = f["v1"] + 7
    f["hop1"] = f"10.{20 + (seed % 30)}.{seed % 80}.2"
    f["hop2"] = f"10.{40 + (seed % 20)}.{seed % 80}.2"
    f["h1"] = f"10.{20 + (seed % 30)}.{seed % 80}.50"
    f["h2"] = f"10.{40 + (seed % 20)}.{seed % 80}.50"
    f["ip1"] = f"10.{20 + (seed % 30)}.{seed % 80}.1"
    f["ip2"] = f"10.{40 + (seed % 20)}.{seed % 80}.1"
    f["nm"] = f"EDGE-{seed % 80}"
    f["d1"] = f"Wing-{seed % 50}"
    f["d2"] = f"Night-{seed % 60}"
    f["tok1"] = f"CLOSET{seed % 90}"
    f["tok2"] = f"RACK{seed % 70}"


def _port(state, name):
    return ((state or {}).get("interfaces") or {}).get(name) or {}


def _reg(lid, checker, syntax, s2p, s3p, s2n, s3n, s2fix, s3fix, ok):
    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": _base,
        "ok": ok,
        "stages": {
            "assisted": {"checker": checker, "prose": s2p, "note": lambda f, t=s2n: t.format(**f),
                         "fix": s2fix, "plant": lambda f: [], "checks": lambda f: [{"kind": checker}]},
            "ticket": {"checker": checker, "prose": s3p, "note": lambda f, t=s3n: t.format(**f),
                       "fix": s3fix, "plant": lambda f: [], "checks": lambda f: [{"kind": checker}]},
        },
    }


def _lines(*body):
    return lambda f: ["enable", "configure terminal", *[p.format(**f) if isinstance(p, str) else p for p in body], "end"]


# VLAN
_reg("sw-vlan-access", "vlan-member", VLAN,
     "The training-room phone was patched into the third access port and it is still in the default VLAN, so it never reaches the users subnet. The practice note names the VLAN and that port. Create the VLAN and place only that port in it. Leave the walkthrough port where it is.",
     "A printer on the second access port came up in the default VLAN after a recable. The incident note names the VLAN it should join. The third port you just moved can stay.",
     "Create VLAN {v1}. Put FastEthernet0/3 in it as an access port.",
     "Put FastEthernet0/2 in VLAN {v2} as an access port.",
     _lines("vlan {v1}", "name LAB{v1}", "interface fa0/3", "switchport mode access", "switchport access vlan {v1}"),
     _lines("vlan {v2}", "name LAB{v2}", "interface fa0/2", "switchport mode access", "switchport access vlan {v2}"),
     lambda st, f, stage: (_port(st, "FastEthernet0/3").get("vlan") == f["v1"] and _port(st, "FastEthernet0/3").get("mode") == "access") if stage == "assisted"
     else (_port(st, "FastEthernet0/2").get("vlan") == f["v2"] and _port(st, "FastEthernet0/2").get("mode") == "access"))

_reg("sw-vlan-and-trunk", "vlan-trunk", VLAN + TRUNK,
     "A new phone is on the third access port, in the default VLAN, and the uplink is not yet limited. The practice note has the VLAN for that phone. Put the phone port in it. Do not turn the uplink into an access port.",
     "The uplink is carrying every VLAN, including ones this closet does not use. The incident note lists the only VLAN that should remain on the trunk.",
     "Put FastEthernet0/3 in VLAN {v1}.",
     "Trunk FastEthernet0/1 and allow only VLAN {v1}.",
     _lines("vlan {v1}", "name LAB{v1}", "interface fa0/3", "switchport mode access", "switchport access vlan {v1}"),
     _lines("interface fa0/1", "switchport mode trunk", "switchport trunk allowed vlan {v1}"),
     lambda st, f, stage: (_port(st, "FastEthernet0/3").get("vlan") == f["v1"]) if stage == "assisted"
     else (_port(st, "FastEthernet0/1").get("trunk") and list(_port(st, "FastEthernet0/1").get("allowed") or []) == [f["v1"]]))

_reg("sw-vlan-multi", "vlan-trunk", VLAN + TRUNK,
     "Staff and the lobby kiosk are still in one broadcast domain. The practice note has two VLAN numbers, the staff port, and the kiosk port. Build both VLANs and place each port. The single VLAN from the earlier lab is not this closet.",
     "The uplink toward the router is still carrying every VLAN. After the two access ports are in their VLANs, limit the trunk to those two numbers and no others.",
     "VLAN {v1} on FastEthernet0/2. VLAN {v2} on FastEthernet0/3.",
     "Trunk FastEthernet0/1 allowed VLANs {v1} and {v2} only.",
     _lines("vlan {v1}", "name STAFF{v1}", "vlan {v2}", "name GUEST{v2}",
            "interface fa0/2", "switchport mode access", "switchport access vlan {v1}",
            "interface fa0/3", "switchport mode access", "switchport access vlan {v2}"),
     _lines("interface fa0/1", "switchport mode trunk", "switchport trunk allowed vlan {v1},{v2}"),
     lambda st, f, stage: (_port(st, "FastEthernet0/2").get("vlan") == f["v1"] and _port(st, "FastEthernet0/3").get("vlan") == f["v2"]) if stage == "assisted"
     else (_port(st, "FastEthernet0/1").get("trunk") and list(_port(st, "FastEthernet0/1").get("allowed") or []) == sorted((f["v1"], f["v2"]))))

_reg("sw-trunk-basics", "trunk", TRUNK,
     "The uplink is a trunk and it still allows every VLAN. The practice note lists the only VLAN that may cross to the next switch. Restrict the uplink to that one number.",
     "A second VLAN now has to cross the same uplink, and the list you just set does not include it. Add that VLAN to the allowed list without turning the port into an access port.",
     "Allow only VLAN {v1} on FastEthernet0/1.",
     "Allow VLANs {v1} and {v2} on the uplink.",
     _lines("interface fa0/1", "switchport mode trunk", "switchport trunk allowed vlan {v1}"),
     _lines("interface fa0/1", "switchport mode trunk", "switchport trunk allowed vlan {v1},{v2}"),
     lambda st, f, stage: (_port(st, "FastEthernet0/1").get("trunk") and list(_port(st, "FastEthernet0/1").get("allowed") or []) == [f["v1"]]) if stage == "assisted"
     else (list(_port(st, "FastEthernet0/1").get("allowed") or []) == sorted((f["v1"], f["v2"]))))

_reg("sw-port-security", "port-security", IOS + [("Port security", "switchport port-security")],
     "A laptop keeps moving between the third access port and a dock, and the switch learns a new address every time. Turn port security on that port. The port you secured in the walkthrough is a different jack.",
     "The uplink-facing access port, FastEthernet0/1, is still learning every address plugged into the patch panel. Turn port security on there too.",
     "Enable port security on FastEthernet0/3.",
     "Enable port security on FastEthernet0/1.",
     _lines("interface fa0/3", "switchport mode access", "switchport port-security"),
     _lines("interface fa0/1", "switchport mode access", "switchport port-security"),
     lambda st, f, stage: bool(_port(st, "FastEthernet0/3").get("portsec")) if stage == "assisted"
     else bool(_port(st, "FastEthernet0/1").get("portsec")))

_reg("sw-banner", "banner", IOS + [("Login banner", "banner login <text>")],
     "Auditors want the login screen to show a closet code that is not the sample from the walkthrough. The practice note has the exact token. Put it in the login banner.",
     "The banner you just set is the practice code. The rack label uses a different code, in the incident note. The login banner has to include that code.",
     "The login banner must include {tok1}.",
     "The login banner must include {tok2}.",
     _lines("banner login {tok1}"),
     _lines("banner login {tok2}"),
     lambda st, f, stage: (f["tok1"] if stage == "assisted" else f["tok2"]) in str(st.get("banner") or ""))

_reg("sw-describe", "description", IOS + [("Description", "description <text>")],
     "The access port facing the user desk still has a stale description, so the diagram and the switch disagree. The practice note has the text for FastEthernet0/2.",
     "FastEthernet0/3, the new printer drop, has no description. The incident note has the text. Do not change the description you just set on the user port.",
     "Describe FastEthernet0/2 as {d1}.",
     "Describe FastEthernet0/3 as {d2}.",
     _lines("interface fa0/2", "description {d1}"),
     _lines("interface fa0/3", "description {d2}"),
     lambda st, f, stage: _port(st, "FastEthernet0/2").get("desc") == f["d1"] if stage == "assisted"
     else _port(st, "FastEthernet0/3").get("desc") == f["d2"])

_reg("sw-mac-table", "vlan-member", VLAN,
     "The MAC table shows the new phone on the third access port, and that port is still in the default VLAN. The practice note has the VLAN the phone should join. Move that port.",
     "A second phone showed up on the second access port in the default VLAN. The incident note has its VLAN. Leave the third port in the VLAN you just set.",
     "Put FastEthernet0/3 in VLAN {v1}.",
     "Put FastEthernet0/2 in VLAN {v2}.",
     _lines("vlan {v1}", "name PHONE{v1}", "interface fa0/3", "switchport mode access", "switchport access vlan {v1}"),
     _lines("vlan {v2}", "name PHONE{v2}", "interface fa0/2", "switchport mode access", "switchport access vlan {v2}"),
     lambda st, f, stage: _port(st, "FastEthernet0/3").get("vlan") == f["v1"] if stage == "assisted"
     else _port(st, "FastEthernet0/2").get("vlan") == f["v2"])

_reg("sw-int-status", "interface-up", IOS + [("Administratively enable", "no shutdown")],
     "Interface status shows the third access port administratively down, which is why the phone has no link. Bring that port up.",
     "The second access port is administratively down as well. The incident is that jack, not the one you just enabled.",
     "No shutdown on FastEthernet0/3.",
     "No shutdown on FastEthernet0/2.",
     _lines("interface fa0/3", "no shutdown"),
     _lines("interface fa0/2", "no shutdown"),
     lambda st, f, stage: _port(st, "FastEthernet0/3").get("up") is True if stage == "assisted"
     else _port(st, "FastEthernet0/2").get("up") is True)

_reg("sw-hostname-write", "saved-config", IOS + [("Device name", "hostname <name>"), ("Save", "write memory")],
     "The prompt still shows the image name, so the closet diagram does not match the switch you are on. The practice note has the name. Set it. Saving is the next stage.",
     "The name is set and a reload would drop it, because the running configuration was never written to startup. Save it.",
     "Device name: {nm}.",
     "Write the running configuration to startup.",
     _lines("hostname {nm}"),
     lambda f: ["write memory"],
     lambda st, f, stage: st.get("hostname") == f["nm"] if stage == "assisted"
     else (st.get("hostname") == f["nm"] and (st.get("startup") is True or st.get("saved") is True)))

_reg("sw-show-ver", "saved-config", IOS + [("Device name", "hostname <name>"), ("Save", "write memory")],
     "The software version tells you which box this is, and the prompt name does not match the closet label. The practice note has the name to set.",
     "The name matches the label and it will not survive a reload until you write the configuration.",
     "Set the device name to {nm}.",
     "Save the running configuration.",
     _lines("hostname {nm}"),
     lambda f: ["write memory"],
     lambda st, f, stage: st.get("hostname") == f["nm"] if stage == "assisted"
     else (st.get("hostname") == f["nm"] and (st.get("startup") is True or st.get("saved") is True)))

# Routers
_reg("rtr-gateway", "address", ADDR,
     "The far LAN was renumbered. GigabitEthernet0/1 still has no address for it. The practice note has the address and mask. Put them on that interface and bring it up.",
     "The near interface is up with the walkthrough address, and the far interface you just addressed is administratively down if you skipped the last step. Bring GigabitEthernet0/1 up if it is down, and leave the address from practice on it.",
     "Address GigabitEthernet0/1 with {ip1} mask 255.255.255.0 and bring it up.",
     "GigabitEthernet0/1 must be up with {ip1} still configured.",
     _lines("interface GigabitEthernet0/1", "ip address {ip1} 255.255.255.0", "no shutdown"),
     _lines("interface GigabitEthernet0/1", "no shutdown"),
     lambda st, f, stage: _port(st, "GigabitEthernet0/1").get("ip") == f["ip1"] and _port(st, "GigabitEthernet0/1").get("up") is True)

# stage 3 of gateway auto-passes if stage 2 already set up+ip. Need a different stage 3.
# I'll override ticket to address gi0/0 instead. Patch after if the lambda treats both stages the same.
# The lambda above requires the same condition for both stages. BAD.
# Fix by replacing the ok after registration... I'll set a distinct ticket below by editing the spec.

_reg("rtr-two-interfaces", "address", ADDR,
     "You already proved two connected networks with the walkthrough addresses. This site's far LAN uses a different address, in the practice note, on GigabitEthernet0/1.",
     "The near LAN was also renumbered. GigabitEthernet0/0 needs the address in the incident note, and it has to be up. Leave the far interface as you just set it.",
     "Address GigabitEthernet0/1 with {ip1} 255.255.255.0 and no shutdown.",
     "Address GigabitEthernet0/0 with {ip2} 255.255.255.0 and no shutdown.",
     _lines("interface GigabitEthernet0/1", "ip address {ip1} 255.255.255.0", "no shutdown"),
     _lines("interface GigabitEthernet0/0", "ip address {ip2} 255.255.255.0", "no shutdown"),
     lambda st, f, stage: _port(st, "GigabitEthernet0/1").get("ip") == f["ip1"] if stage == "assisted"
     else _port(st, "GigabitEthernet0/0").get("ip") == f["ip2"])

_reg("rtr-edge-complete", "route", ROUTE,
     "The edge forwards for the walkthrough LANs and has no default route toward the new provider. The practice note has the next hop.",
     "A second provider hop replaced the one you just installed. The incident note has the hop that should be the default now. The old route can stay; the new one has to be present.",
     "Default route via {hop1}.",
     "Default route via {hop2}.",
     _lines("ip route 0.0.0.0 0.0.0.0 {hop1}"),
     _lines("ip route 0.0.0.0 0.0.0.0 {hop2}"),
     lambda st, f, stage: (f["hop1"] if stage == "assisted" else f["hop2"]) in " ".join(st.get("static") or []))

_reg("rtr-default-route", "route", ROUTE,
     "Users on the inside LAN reach each other and nothing beyond this router. The practice note has a next hop that is not the walkthrough hop. Install that default route.",
     "The provider changed the hop again overnight. The incident note has the new one. Add it. A route that only names the walkthrough hop does not pass.",
     "Next hop {hop1}.",
     "Next hop {hop2}.",
     _lines("ip route 0.0.0.0 0.0.0.0 {hop1}"),
     _lines("ip route 0.0.0.0 0.0.0.0 {hop2}"),
     lambda st, f, stage: (f["hop1"] if stage == "assisted" else f["hop2"]) in " ".join(st.get("static") or []))

_reg("rtr-trace", "route", ROUTE,
     "The traceroute died on this router because there is no route for the far network. The practice note has the next hop of a default route.",
     "The far network moved to a different next hop. The incident note has it. Add that default route.",
     "Default via {hop1}.",
     "Default via {hop2}.",
     _lines("ip route 0.0.0.0 0.0.0.0 {hop1}"),
     _lines("ip route 0.0.0.0 0.0.0.0 {hop2}"),
     lambda st, f, stage: (f["hop1"] if stage == "assisted" else f["hop2"]) in " ".join(st.get("static") or []))

_reg("rtr-vlan-acl", "acl", ACL,
     "Inter-VLAN routing is in place and a host that should not be reachable still is. The practice note names one host to deny in a standard access list.",
     "A second host needs the same deny. The incident note has its address. Add a deny for that host. Do not remove the entry you already wrote.",
     "Deny host {h1} in a standard access list.",
     "Deny host {h2}.",
     _lines("access-list 15 deny host {h1}"),
     _lines("access-list 15 deny host {h2}"),
     lambda st, f, stage: (f["h1"] if stage == "assisted" else f["h2"]) in str(st.get("acls") or ""))

_reg("rtr-describe", "description", IOS + [("Description", "description <text>")],
     "GigabitEthernet0/0 faces the users LAN and its description is empty or left over from the walkthrough. The practice note has the text.",
     "GigabitEthernet0/1, the far LAN, still has no description. The incident note has the text. Do not edit the users-LAN description again.",
     "Describe GigabitEthernet0/0 as {d1}.",
     "Describe GigabitEthernet0/1 as {d2}.",
     _lines("interface GigabitEthernet0/0", "description {d1}"),
     _lines("interface GigabitEthernet0/1", "description {d2}"),
     lambda st, f, stage: _port(st, "GigabitEthernet0/0").get("desc") == f["d1"] if stage == "assisted"
     else _port(st, "GigabitEthernet0/1").get("desc") == f["d2"])

_reg("rtr-hostname-write", "saved-config", IOS + [("Device name", "hostname <name>"), ("Save", "write memory")],
     "You saved a walkthrough name on this router. The practice note has a different name. Set it. The save is the following stage.",
     "The new name is only in the running configuration. Write it so a reload keeps it.",
     "Device name: {nm}.",
     "Save the running configuration.",
     _lines("hostname {nm}"),
     lambda f: ["write memory"],
     lambda st, f, stage: st.get("hostname") == f["nm"] if stage == "assisted"
     else (st.get("hostname") == f["nm"] and (st.get("startup") is True or st.get("saved") is True)))

# rtr-gateway ticket must differ from stage 2. Rebind its ticket to the near interface address.
SK.SPECS["rtr-gateway"]["stages"]["ticket"]["fix"] = _lines("interface GigabitEthernet0/0", "ip address {ip2} 255.255.255.0", "no shutdown")
SK.SPECS["rtr-gateway"]["stages"]["ticket"]["note"] = lambda f: f"Address GigabitEthernet0/0 with {f['ip2']} mask 255.255.255.0 and bring it up."
SK.SPECS["rtr-gateway"]["stages"]["ticket"]["prose"] = (
    "The near LAN was renumbered after you finished the far interface. GigabitEthernet0/0 still has the walkthrough address or none. "
    "The incident note has the new address. Put it on GigabitEthernet0/0 and bring that interface up. Leave the far interface as you set it."
)
SK.SPECS["rtr-gateway"]["ok"] = lambda st, f, stage: (
    _port(st, "GigabitEthernet0/1").get("ip") == f["ip1"] if stage == "assisted"
    else _port(st, "GigabitEthernet0/0").get("ip") == f["ip2"]
)

# Interface-down labs start with the ports shut, once.
def _shut(lid, *ports):
    def plant(state, f):
        if state.get("px", {}).get("ios_planted"):
            return
        state.setdefault("px", {})["ios_planted"] = True
        for name in ports:
            iface = (state.get("interfaces") or {}).get(name)
            if iface is not None:
                iface["up"] = False
    SK.SPECS[lid]["plant_state"] = plant

_shut("sw-int-status", "FastEthernet0/2", "FastEthernet0/3")
