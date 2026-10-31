"""Stage 2 and Stage 3 for Windows CLI and Windows desktop labs.

The check is the setting the command changes: resolver, route, firewall,
service, adapter, print queue, wireless profile, or switch. It is not a
computer rename unless the lab is about identity, and then the DNS suffix
has to change as well.
"""
from __future__ import annotations

import lab_skills as SK

WIN = [
    ("Show the address", "ipconfig /all"),
    ("Set the resolver", "the DNS-client cmdlet, with an interface and a server address"),
    ("Renew a lease", "ipconfig /<release-or-renew>"),
    ("Flush the cache", "ipconfig /<flush-option>"),
    ("Ask a name", "nslookup <name>"),
]
ROUTE = [("Show routes", "route print"), ("Add a route", "route add <dest> mask <mask> <gateway>")]
FW = [("Show profiles", "netsh advfirewall show allprofiles"), ("Set a profile", "netsh advfirewall set <profile> state <on|off>")]
SVC = [("Show a service", "Get-Service <name>"), ("Start a service", "Start-Service <name>")]
WLAN = [("Show networks", "netsh wlan show networks"), ("Connect", "netsh wlan connect name=<profile>")]


def _seed_ip(seed, third):
    return f"10.{20 + (seed % 40)}.{third}.{10 + (seed % 20)}"


def _mark(state):
    return state.setdefault("px", {}).setdefault("mark", {})


def _plant_once(state, **fields):
    px = state.setdefault("px", {})
    if px.get("win_planted"):
        return
    px["win_planted"] = True
    mark = px.setdefault("mark", {})
    mark.update(fields)


def _cmd(lid, checker, syntax, s2_prose, s3_prose, s2_note, s3_note, s2_cmd, s3_cmd, plant_fields, match):
    """match(low, raw, f, state) -> dict of mark fields to set, or None."""

    def enrich(f, seed):
        f["w_ip"] = _seed_ip(seed, 8)
        f["w_ip2"] = _seed_ip(seed, 18)
        f["w_hop"] = _seed_ip(seed, 2)
        f["w_name"] = f"CLINIC-{20 + (seed % 40)}"
        f["w_svc"] = ("W32Time", "EventLog", "LanmanServer", "Schedule", "Sens")[seed % 5]
        f["w_proc"] = ("SearchApp", "msedge", "OneDrive", "WINWORD", "Teams")[seed % 5]
        f["w_acct"] = ("kiosk-front", "lab-tech", "front-desk", "scan-user", "night-audit")[seed % 5]
        f["w_acct2"] = ("kiosk-back", "lab-lead", "front-lead", "scan-lead", "night-lead")[seed % 5]
        f["w_ssid"] = ("Novak-Clinic", "Novak-East", "Novak-Ward", "Novak-Lab", "Novak-Lobby")[seed % 5]
        f["w_suffix"] = f"clinic{20 + (seed % 40)}.local"

    def note(stage):
        text = s2_note if stage == "assisted" else s3_note
        return lambda f: text.format(**f)

    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": enrich,
        "plant_state": lambda state, f: _plant_once(state, **plant_fields(f)),
        "stages": {
            "assisted": {"checker": checker, "prose": s2_prose, "note": note("assisted"),
                         "fix": lambda f: [s2_cmd(f)], "checks": lambda f: [{"kind": checker}]},
            "ticket": {"checker": checker, "prose": s3_prose, "note": note("ticket"),
                       "fix": lambda f: [s3_cmd(f)], "checks": lambda f: [{"kind": checker}]},
        },
        "match": match,
        "ok": lambda state, f, stage: _ok(checker, state, f, stage),
    }


def _ok(checker, state, f, stage):
    mark = (state.get("px") or {}).get("mark") or {}
    dns = [str(x) for x in (state.get("dns") or [])]
    if checker == "dns":
        want = f["w_ip"] if stage == "assisted" else f["w_ip2"]
        return dns == [want]
    if checker == "route":
        return mark.get("hop") == (f["w_hop"] if stage == "assisted" else f["w_ip2"])
    if checker == "firewall":
        return mark.get("fw") == ("all" if stage == "assisted" else "private")
    if checker == "service":
        want = "Spooler" if stage == "assisted" else f["w_svc"]
        return str(mark.get("service") or "").lower() == want.lower()
    if checker == "renew":
        if stage == "assisted":
            return mark.get("renewed") is True
        return dns == [f["w_ip2"]]
    if checker == "flush":
        if stage == "assisted":
            return dns == [f["w_ip"]] and mark.get("flushed") is True
        return mark.get("flushed") is True and dns == [f["w_ip2"]]
    if checker == "wlan":
        want = f["w_ssid"] if stage == "assisted" else "Novak-Staff"
        return str(mark.get("wlan") or "").lower() == want.lower()
    if checker == "print":
        if stage == "assisted":
            return mark.get("queue") == "clear"
        return mark.get("queue") == "clear" and mark.get("service") == "Spooler"
    if checker == "switch":
        want = "Clinic-Internal" if stage == "assisted" else "Lab-Private"
        return str(mark.get("switch") or "").lower() == want.lower()
    if checker == "arp":
        return mark.get("arp") == ("clear" if stage == "assisted" else "one")
    if checker == "disk":
        return mark.get("disk") == ("1" if stage == "assisted" else "2")
    if checker == "process":
        want = "notepad" if stage == "assisted" else f["w_proc"]
        return str(mark.get("killed") or "").lower() == want.lower()
    if checker == "adapter":
        return (state.get("gui") or {}).get("adapter") == "up" or mark.get("adapter") == "up"
    if checker == "updates":
        return (state.get("gui") or {}).get("updates") == "checked"
    if checker == "identity":
        host = (state.get("hostname") or mark.get("hostname") or "").lower()
        if stage == "assisted":
            return host == f["w_name"].lower()
        suffix = (mark.get("suffix") or "").lower()
        return host == f["w_name"].lower() and suffix == f["w_suffix"].lower()
    if checker == "account":
        want = f["w_acct"] if stage == "assisted" else f["w_acct2"]
        return str(mark.get("account") or "").lower() == want.lower()
    if checker == "device":
        return "net" in ((state.get("gui") or {}).get("dev_open") or [])
    if checker == "ad":
        return str(mark.get("ad") or "").lower() == f["w_name"].lower()
    if checker == "port":
        return mark.get("port") == ("587" if stage == "assisted" else "25")
    if checker == "mac":
        if stage == "assisted":
            return mark.get("adapter") == "up"
        return mark.get("arp") == "one"
    if checker == "listen":
        if stage == "assisted":
            return str(mark.get("service") or "").lower() == "spooler"
        return mark.get("fw") == "private"
    if checker == "reach":
        if stage == "assisted":
            return dns == [f["w_ip"]]
        return mark.get("fw") == "private"
    return False


def win_effect(lab, state, raw):
    row = SK.spec(lab)
    if not row or "match" not in row:
        return False
    f = (state.get("px") or {}).get("facts") or {}
    low = " ".join(str(raw).split()).lower()
    changed = row["match"](low, raw, f, state)
    if not changed:
        return False
    _mark(state).update(changed)
    # Keep the resolver list in the same place ipconfig reads.
    if "dns" in changed:
        state["dns"] = [changed["dns"]]
        state["px_dns"] = state["dns"]
    if "hostname" in changed:
        state["hostname"] = changed["hostname"]
        state["px_host"] = changed["hostname"]
    if "adapter" in changed and isinstance(state.get("gui"), dict):
        state["gui"]["adapter"] = changed["adapter"]
    if "updates" in changed and isinstance(state.get("gui"), dict):
        state["gui"]["updates"] = "checked"
    if changed.get("device") and isinstance(state.get("gui"), dict):
        opened = state["gui"].setdefault("dev_open", [])
        if "net" not in opened:
            opened.append("net")
    return True


def apply_desk(lab, state, stage, text):
    """Record a desktop answer when it is the value this stage is grading."""
    row = SK.spec(lab)
    if not row or not row.get("ok"):
        return False
    f = (state.get("px") or {}).get("facts") or {}
    expect = str(row["stages"][stage]["fix"](f)[0]).strip()
    if str(text).strip() != expect:
        return False
    if win_effect(lab, state, text):
        return True
    checker = row["stages"][stage]["checker"]
    mark = _mark(state)
    if checker == "dns":
        state["dns"] = [text]
        state["px_dns"] = state["dns"]
    elif checker == "service":
        mark["service"] = text
    elif checker == "identity" and stage == "assisted":
        state["hostname"] = text
        state["px_host"] = text
    elif checker == "identity":
        mark["suffix"] = text
    elif checker == "ad":
        mark["ad"] = text
    elif checker == "account":
        mark["account"] = text
    else:
        return False
    return True


def win_ok(lab, stage, state, facts):
    row = SK.spec(lab)
    if not row or "ok" not in row:
        return None
    return row["ok"](state, facts, stage)


def desk_answer(lab, facts, stage):
    return None


# match helpers

def _dns_match(low, raw, f, state):
    import re
    m = re.search(r"-serveraddresses\s+(\S+)", raw, re.I)
    if m and "dns" in low:
        return {"dns": m.group(1).strip("'\"")}
    m = re.search(r"set dns\s+\S+\s+static\s+(\S+)", low)
    if m:
        return {"dns": m.group(1)}
    return None


def _route_match(low, raw, f, state):
    import re
    m = re.search(r"route\s+add\s+\S+\s+mask\s+\S+\s+(\S+)", low)
    if m:
        return {"hop": m.group(1)}
    return None


def _fw_match(low, raw, f, state):
    if "advfirewall" in low and "state on" in low:
        return {"fw": "private" if "privateprofile" in low else "all"}
    return None


def _svc_match(low, raw, f, state):
    import re
    m = re.search(r"start-service\s+(\S+)", low)
    if m:
        return {"service": m.group(1)}
    return None


def _renew_match(low, raw, f, state):
    out = {}
    if low == "ipconfig /renew":
        out["renewed"] = True
    dns = _dns_match(low, raw, f, state)
    if dns:
        out.update(dns)
    return out or None


def _flush_match(low, raw, f, state):
    out = {}
    if "flushdns" in low:
        out["flushed"] = True
    dns = _dns_match(low, raw, f, state)
    if dns:
        out.update(dns)
    return out or None


def _wlan_match(low, raw, f, state):
    import re
    m = re.search(r"connect name=(\S+)", low)
    if m:
        return {"wlan": m.group(1)}
    return None


def _print_match(low, raw, f, state):
    out = {}
    if "remove-printjob" in low:
        out["queue"] = "clear"
    if "spooler" in low and ("restart-service" in low or "start-service" in low):
        out["service"] = "Spooler"
    return out or None


def _switch_match(low, raw, f, state):
    import re
    m = re.search(r"new-vmswitch\s+-name\s+(\S+)", low)
    if m:
        return {"switch": m.group(1)}
    return None


def _arp_match(low, raw, f, state):
    import re
    if low.startswith("arp -d"):
        return {"arp": "one" if re.search(r"\d", low) else "clear"}
    return None


def _disk_match(low, raw, f, state):
    if "online disk" in low:
        return {"disk": low.split()[-1]}
    return None


def _proc_match(low, raw, f, state):
    import re
    m = re.search(r"stop-process\s+-name\s+(\S+)", low)
    if m:
        return {"killed": m.group(1)}
    return None


def _adapter_match(low, raw, f, state):
    if low in ("ipconfig /renew", "netsh interface set interface ethernet enable"):
        return {"adapter": "up"}
    return None


def _id_match(low, raw, f, state):
    import re
    out = {}
    m = re.search(r"-newname\s+(\S+)", raw, re.I)
    if m and "rename-computer" in low:
        out["hostname"] = m.group(1).strip("'\"")
    m = re.search(r"set dnssuffix\s+(\S+)", low)
    if m:
        out["suffix"] = m.group(1)
    return out or None


def _acct_match(low, raw, f, state):
    import re
    m = re.search(r"enable-localuser\s+-name\s+(\S+)", low)
    if m:
        return {"account": m.group(1)}
    return None


def _ad_match(low, raw, f, state):
    import re
    m = re.search(r"unlock-adaccount\s+(\S+)", low)
    if m:
        return {"ad": m.group(1)}
    return None


def _port_match(low, raw, f, state):
    import re
    m = re.search(r"-port\s+(\d+)", low)
    if m and "test-netconnection" in low:
        return {"port": m.group(1)}
    return None


def _reg(lid, checker, syntax, s2p, s3p, s2n, s3n, s2c, s3c, plant, match):
    _cmd(lid, checker, syntax, s2p, s3p, s2n, s3n, s2c, s3c, plant, match)


# DNS labs. Each story is a different failure, and the graded state is the resolver list.
_reg("win-dns-break", "dns", WIN,
     "A new application host was added overnight and this PC still asks the resolver that does not know it. The practice note has the one DNS server that does. Point Ethernet at that server and leave the address on DHCP.",
     "Names for the clinic app still fail, and the address answers. The resolver list on Ethernet is the old pair. The server that holds the record now is not in this sentence.",
     "DNS server for Ethernet: {w_ip}. Leave DHCP in charge of the address.",
     "The app name fails. Get-Content ticket.txt prints the only DNS server Ethernet should use.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-net-cli", "dns", WIN,
     "You already showed that a name fails while an address works, using the image resolvers. The practice note names the server that actually has the record. Make that the only DNS server on Ethernet.",
     "The failing name still does not resolve. The DNS server list was never changed.",
     "Set Ethernet DNS to {w_ip}.",
     "Names still fail. The only line in ticket.txt is the server Ethernet should ask. Read it with Get-Content ticket.txt.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-nslookup-ok", "dns", WIN,
     "The walkthrough lookup used the image DNS servers. Those servers are being retired. The practice note has the replacement. Make it the only server on Ethernet.",
     "Lookups still go to a server that is about to be switched off.",
     "Resolver to configure: {w_ip}.",
     "The replacement resolver is the only line of ticket.txt. Point Ethernet at it.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-ipconfig", "dns", WIN,
     "The full address listing on this PC still shows the image DNS servers, and the charting name will not resolve. The practice note has the server this adapter should use. Set that and leave the address on automatic.",
     "The identity you recorded is stale because the resolver changed this morning.",
     "Ethernet DNS: {w_ip}.",
     "Ethernet should use the DNS server in ticket.txt. The address stays on DHCP. Read the file with Get-Content ticket.txt.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("w11-powershell-net", "dns", WIN,
     "The address view from the shell showed the image DNS servers. The practice note has the server the branch file share was moved to. Set that on Ethernet.",
     "The branch share still fails by name. The resolver list was not updated.",
     "Set the Ethernet resolver to {w_ip}.",
     "The share's resolver is the only address in ticket.txt.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("w11-netsh", "dns", WIN,
     "Both address tools showed the image DNS servers. The practice note has the server this site published. Set it with the DNS cmdlet. Leave the address on DHCP.",
     "The older interface tool and ipconfig still disagree with the site's resolver.",
     "DNS server: {w_ip}.",
     "Point Ethernet at the address printed by Get-Content ticket.txt.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("gui-ethernet", "dns", WIN,
     "Ethernet properties still list the image DNS servers. The practice note has the resolver for this moved desk. Set that server. Leave the address automatic.",
     "The desk was moved again and the resolver in Ethernet properties is the practice one, which this wing does not use.",
     "In Ethernet, set DNS to {w_ip}.",
     "Open Ethernet and set DNS to the address in ticket.txt.",
     lambda f: f["w_ip"], lambda f: f["w_ip2"], lambda f: {}, _dns_match)

_reg("scn-dns-evidence", "dns", WIN,
     "The third-floor caller can open the proxy by address and nothing by name. This PC is the evidence station. The practice note has the DNS server that should hold the intranet record. Point Ethernet at it.",
     "The name still fails after the first change.",
     "Evidence PC DNS: {w_ip}.",
     "The floor resolver is the only line in ticket.txt. Get-Content ticket.txt prints it.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-flushdns", "flush", WIN,
     "You cleared the cache and it filled again from the same retired server. The practice note has the server to configure, and the cache has to be cleared after that change or the old answer sticks.",
     "The name fails again because the cache was filled from the retired server. ticket.txt has the replacement server. Set that, then flush.",
     "Set DNS to {w_ip}, then flush the cache.",
     "The replacement DNS server is the only line in ticket.txt. Set it, then flush. The practice server is retired.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {"flushed": False}, _flush_match)

# flush stage 3 only sets flushed, but _ok for flush requires dns == w_ip AND flushed.
# Stage 3 command is only flush. Stage 2 sets dns. If both must be true at stage 3, stage 2's dns must remain.
# Stage 3 check uses w_ip not w_ip2. Good if stage 2 already set dns. Plant doesn't clear dns.
# Stage 3 fix is only flush. Student must have set DNS in stage 2. Solver runs stage 2 first. Good.

_reg("win-dhcp-renew", "renew", WIN,
     "Cycling the lease brought back the image DNS servers. The practice note has the resolver this lease should keep. Renew, and set that DNS server.",
     "The laptop still holds Friday's resolver after the LAN came back. Renew the lease, then set the DNS server from ticket.txt.",
     "Renew the lease and set DNS to {w_ip}.",
     "Renew, then set DNS to the only address in ticket.txt.",
     lambda f: "ipconfig /renew",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {"renewed": False}, _renew_match)

_reg("scn-lan2-verify", "renew", WIN,
     "The CFO laptop still has Friday's resolver. Renew the lease and set the DNS server in the practice note.",
     "The laptop got a new lease and is still asking the old resolver.",
     "Renew the lease.",
     "After the renew, DNS should be the address in ticket.txt.",
     lambda f: "ipconfig /renew",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {"renewed": False}, _renew_match)

_reg("win-full-triage", "dns", WIN,
     "The full triage used the image DNS pair. This desk moved to a wing whose resolver is in the practice note. Set that server. Keep the address on DHCP.",
     "Lookups still use the wing you moved away from.",
     "Wing resolver: {w_ip}.",
     "This wing's resolver is the only line in ticket.txt.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-route", "route", ROUTE,
     "The route table shows a default gateway that no longer forwards. The practice note has the next hop to install for 0.0.0.0. Add that route. Do not delete the connected subnet.",
     "Traffic off the subnet dies on this PC. The default route is missing or points at the old hop.",
     "Add a default route via {w_hop}.",
     "The default gateway to add is the only line in ticket.txt. Read it with Get-Content ticket.txt.",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_hop']}",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_ip2']}",
     lambda f: {"hop": ""}, _route_match)

_reg("win-ping-loop", "route", ROUTE,
     "Loopback answers, so the stack is up. Anything past the local subnet does not, because there is no default route. The practice note has the hop.",
     "Ping to the gateway times out and loopback still answers.",
     "Default hop: {w_hop}.",
     "Install a default route via the hop in ticket.txt.",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_hop']}",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_ip2']}",
     lambda f: {"hop": ""}, _route_match)

_reg("w11-firewall", "firewall", FW,
     "The profiles were on in the walkthrough and someone turned the domain profile off while chasing a share. The practice task is to turn every profile on. Do not add an allow for the share.",
     "The private profile was left off after the all-profiles change, and a laptop on that profile can reach a share it should not. Turn the private profile on.",
     "Set all firewall profiles on.",
     "The private firewall profile is off. Turn that profile on.",
     lambda f: "netsh advfirewall set allprofiles state on",
     lambda f: "netsh advfirewall set privateprofile state on",
     lambda f: {"fw": "off"}, _fw_match)

_reg("w11-services", "service", SVC,
     "DHCP, the DNS client, and Defender are running. The print spooler is stopped, which is why nothing prints. The practice note names the service to start.",
     "A service other than the spooler is stopped. ticket.txt names it. Start that one. Do not stop Defender.",
     "Start the Spooler service.",
     "Start the service named in ticket.txt. Get-Content ticket.txt prints the service name.",
     lambda f: "Start-Service Spooler",
     lambda f: f"Start-Service {f['w_svc']}",
     lambda f: {"service": ""}, _svc_match)

_reg("gui-services", "service", SVC,
     "Services shows the spooler stopped. Start the service named in the practice note.",
     "Another service the desk depends on is stopped. The incident note names it. Start that service.",
     "Start Spooler.",
     "Start {w_name}.",
     lambda f: "Spooler",
     lambda f: f["w_name"],
     lambda f: {"service": ""}, _svc_match)

_reg("print-trouble", "print", SVC + [("Queue", "Get-PrintJob -PrinterName <name>"), ("Remove one job", "Remove-PrintJob -PrinterName <name> -ID <id>")],
     "The HR queue has a job stuck in error and the spooler is running, so the bad job stays. Remove that job and restart the spooler. Do not delete the other jobs by clearing the whole queue.",
     "Jobs are stuck again and the spooler did not come back. Clear the error job and make sure the spooler is running.",
     "Remove the error job and restart Spooler.",
     "The error job is still in the queue and the spooler may be stopped. Clear the job and start Spooler.",
     lambda f: "Remove-PrintJob -PrinterName HR-LaserJet -ID 7",
     lambda f: "Restart-Service Spooler",
     lambda f: {"queue": "error", "service": ""}, _print_match)

# print stage 3 only restarts spooler. Check requires queue clear AND spooler.
# Stage 2 sets queue. Stage 3 sets service. Both must remain. Plant sets queue error and service empty.
# Stage 2 fix only sets queue. Stage 3 sets service. After both, ok. Good.
# But stage 2 check requires BOTH queue and service. Stage 2 won't pass until both are set.
# I need stage 2 check to be only queue, stage 3 both. _ok doesn't distinguish.
# Change print _ok: assisted needs queue clear; ticket needs queue and service.

_reg("w11-wlan", "wlan", WLAN,
     "The wireless report shows this laptop is not on the staff network. The practice note has the profile to join.",
     "The laptop fell back to a guest network. ticket.txt names the profile it should be on.",
     "Connect to {w_ssid}.",
     "Connect to the profile named in ticket.txt.",
     lambda f: f"netsh wlan connect name={f['w_ssid']}",
     lambda f: "netsh wlan connect name=Novak-Staff",
     lambda f: {"wlan": ""}, _wlan_match)

_reg("win-wifi-survey", "wlan", WLAN,
     "The survey shows the laptop associated to a neighboring office. The practice note has the profile this building uses.",
     "After the survey the laptop is on the guest SSID again.",
     "Join {w_ssid}.",
     "Join the profile in ticket.txt. Get-Content ticket.txt prints the SSID.",
     lambda f: f"netsh wlan connect name={f['w_ssid']}",
     lambda f: "netsh wlan connect name=Novak-Staff",
     lambda f: {"wlan": ""}, _wlan_match)

_reg("win-arp", "arp", [("Show ARP", "arp -a"), ("Delete entries", "arp -d *")],
     "The ARP cache still has the old gateway after the router was replaced, so packets go to a stale MAC. Clear the cache.",
     "The cache was cleared and the retired gateway was learned again for one address. Delete that one entry. Do not add a static entry for the old MAC.",
     "Clear the ARP cache.",
     "Delete only the stale gateway entry.",
     lambda f: "arp -d *",
     lambda f: f"arp -d {f['w_hop']}",
     lambda f: {"arp": ""}, _arp_match)

_reg("w11-disk", "disk", [("List disks", "list disk"), ("Bring a disk online", "online disk <number>")],
     "The disk list shows disk 1 offline, which is the data volume. Bring disk 1 online. Do not clean it.",
     "Disk 2, the archive volume, is offline after the reboot. Bring disk 2 online. Leave disk 1 as it is.",
     "Online disk 1.",
     "Disk 2 is offline. Bring it online.",
     lambda f: "online disk 1",
     lambda f: "online disk 2",
     lambda f: {"disk": "offline"}, _disk_match)

_reg("w11-processes", "process", [("List processes", "Get-Process"), ("Stop one", "Stop-Process -Name <name>")],
     "A notepad process is stuck and holding a file the user needs. Stop that process. Do not stop the DNS client.",
     "Another process is stuck and holding a file. ticket.txt names it. Stop that one.",
     "Stop notepad.",
     "Stop the process named in ticket.txt.",
     lambda f: "Stop-Process -Name notepad",
     lambda f: f"Stop-Process -Name {f['w_proc']}",
     lambda f: {"killed": ""}, _proc_match)

_reg("hv-vswitch", "switch", [("List switches", "Get-VMSwitch"), ("Create one", "New-VMSwitch -Name <name> -SwitchType Private")],
     "The lab guests are still on the default switch. The practice note has the private switch to create.",
     "The private switch from practice is not the one the change record names.",
     "Create a private switch named Clinic-Internal.",
     "Create the private switch named in ticket.txt.",
     lambda f: "New-VMSwitch -Name Clinic-Internal -SwitchType Private",
     lambda f: "New-VMSwitch -Name Lab-Private -SwitchType Private",
     lambda f: {"switch": ""}, _switch_match)

def _mac_match(low, raw, f, state):
    hit = _adapter_match(low, raw, f, state)
    if hit:
        return hit
    return _arp_match(low, raw, f, state)


_reg("win-getmac", "mac", [("Show the MAC", "getmac"), ("Enable the adapter", "netsh interface set interface Ethernet enable"), ("Delete one ARP entry", "arp -d <address>")],
     "getmac shows Ethernet as media disconnected because the adapter is disabled. Enable it. The MAC does not change.",
     "Ethernet is up and the asset system still has the old gateway MAC. Delete that one ARP entry. The address is the only line in ticket.txt. Do not clear the whole cache.",
     "Enable Ethernet.",
     "Delete the stale gateway ARP entry. Get-Content ticket.txt prints the address. Do not run arp -d *.",
     lambda f: "netsh interface set interface Ethernet enable",
     lambda f: f"arp -d {f['w_hop']}",
     lambda f: {"adapter": "down", "arp": ""}, _mac_match)

_reg("gui-renew", "adapter", [("Renew", "ipconfig /renew")],
     "The lease on this desk is from the old VLAN. Renew it so the adapter comes back up on the new scope.",
     "The adapter is up on the old lease again. Renew it.",
     "Renew the lease.",
     "Renew the DHCP lease.",
     lambda f: "ipconfig /renew",
     lambda f: "ipconfig /renew",
     lambda f: {"adapter": "down"}, _adapter_match)

_reg("win-hostname", "identity", WIN + [("Computer name", "Rename-Computer -NewName <name>"), ("DNS suffix", "netsh interface ip set dnsSuffix <suffix>")],
     "The name and the DNS suffix still match the image, so two PCs answer the same name. The practice note has the name and the suffix.",
     "The computer name is updated and the DNS suffix is still the image suffix, so two names collide in DNS. ticket.txt has the suffix to set.",
     "Name: {w_name}. Suffix: {w_suffix}.",
     "Keep the name from practice. Set the DNS suffix to the only line in ticket.txt.",
     lambda f: f"Rename-Computer -NewName {f['w_name']}",
     lambda f: f"netsh interface ip set dnsSuffix {f['w_suffix']}",
     lambda f: {"suffix": ""}, _id_match)

# identity check needs BOTH hostname and suffix. Stage 2 only renames. Stage 3 only sets suffix.
# _ok requires both. Stage 2 fails until both exist. Solver runs stage 2 then 3, but stage 2 observe happens before stage 3.
# Stage 2 won't latch. I need _ok for identity: assisted checks hostname, ticket checks both.

_reg("w11-inventory", "identity", WIN,
     "The inventory still shows the image name and an empty DNS suffix. The practice note has the name. Set it.",
     "The name is updated and the suffix is still empty, so the inventory row does not match the domain.",
     "Set the computer name to {w_name}.",
     "Set the DNS suffix to the only line in ticket.txt.",
     lambda f: f"Rename-Computer -NewName {f['w_name']}",
     lambda f: f"netsh interface ip set dnsSuffix {f['w_suffix']}",
     lambda f: {"suffix": ""}, _id_match)

_reg("gui-about", "identity", WIN,
     "About shows the image name. The practice note has the name this desk should carry.",
     "The name is right and the DNS suffix on this PC is still blank, so About's full name is wrong. Set the suffix from the incident note.",
     "Computer name: {w_name}.",
     "DNS suffix: {w_suffix}.",
     lambda f: f["w_name"],
     lambda f: f["w_suffix"],
     lambda f: {"suffix": ""}, _id_match)

_reg("gui-accounts", "account", [("Local account", "Enable-LocalUser -Name <name>")],
     "The kiosk account is disabled. The practice note names it. Enable that account.",
     "A second account, named in the incident note, is disabled. Enable it. Do not disable the kiosk account.",
     "Enable {w_name}.",
     "Enable {w_name}b.",
     lambda f: f"Enable-LocalUser -Name {f['w_name']}",
     lambda f: f"Enable-LocalUser -Name {f['w_name']}b",
     lambda f: {"account": ""}, _acct_match)

_reg("win-ad-users", "ad", [("Directory account", "Unlock-ADAccount <name>")],
     "The walkthrough accounts are in place. The practice note names an account that is still locked. Unlock it.",
     "Another account locked overnight. The incident note names it. Unlock that account.",
     "Unlock {w_name}.",
     "Unlock {w_name}.",
     lambda f: f["w_name"],
     lambda f: f["w_name"],
     lambda f: {"ad": ""}, _ad_match)

_reg("gui-update", "updates", [("Check", "update check")],
     "Windows Update has not been checked on this image. Run the check. Do not install an optional driver.",
     "The last check is from the image build date. Check again.",
     "Check for updates.",
     "Check for updates again. The image date does not count.",
     lambda f: "update check",
     lambda f: "update check",
     lambda f: {}, lambda low, raw, f, state: {"updates": True} if "update" in low and "check" in low else None)

_reg("gui-devices", "device", [("Device Manager", "open the network adapters")],
     "Device Manager has not been opened to the network adapters, so you cannot confirm the NIC the ticket names. Open that category.",
     "The network adapters category is collapsed again. Open it and leave the display adapter alone.",
     "Open network adapters.",
     "Open the network adapters category.",
     lambda f: "net",
     lambda f: "net",
     lambda f: {}, lambda low, raw, f, state: {"device": True} if low == "net" else None)

def _listen_match(low, raw, f, state):
    hit = _svc_match(low, raw, f, state)
    if hit:
        return hit
    return _fw_match(low, raw, f, state)


_reg("win-netstat", "listen", [("Connections", "netstat -ano"), ("Start a service", "Start-Service <name>"), ("Firewall profile", "netsh advfirewall set <profile> state on")],
     "netstat shows nothing listening because the print spooler is stopped. Start Spooler. A connection test is not the repair.",
     "The spooler is running and the private firewall profile is still off, so the port the ticket needs stays closed. Turn the private profile on.",
     "Start the Spooler service.",
     "Turn the private firewall profile on. Do not run Test-NetConnection and call that the fix.",
     lambda f: "Start-Service Spooler",
     lambda f: "netsh advfirewall set privateprofile state on",
     lambda f: {"service": "", "fw": "off"}, _listen_match)

def _reach_match(low, raw, f, state):
    hit = _dns_match(low, raw, f, state)
    if hit:
        return hit
    return _fw_match(low, raw, f, state)


_reg("win-laptop-ports", "reach", [("Resolver", "Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses <address>"), ("Firewall profile", "netsh advfirewall set privateprofile state on")],
     "The laptop cannot resolve the mail host. The practice note has the DNS server to set on Ethernet. A port probe does not fix a name that fails.",
     "The name resolves and the connection still dies. The private firewall profile is off. Turn that profile on.",
     "Set Ethernet DNS to {w_ip}.",
     "Turn the private firewall profile on. The DNS change from practice is already done.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: "netsh advfirewall set privateprofile state on",
     lambda f: {"fw": "off"}, _reach_match)


SK.SPECS["win-flushdns"]["stages"]["assisted"]["fix"] = lambda f: [
    f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
    "ipconfig /flushdns",
]
SK.SPECS["win-flushdns"]["stages"]["ticket"]["fix"] = lambda f: [
    f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
    "ipconfig /flushdns",
]


def _clue(lid, fn):
    SK.SPECS[lid]["clue"] = fn


for _lid in (
    "win-dns-break", "win-net-cli", "win-nslookup-ok", "win-ipconfig", "w11-powershell-net",
    "w11-netsh", "scn-dns-evidence", "win-flushdns", "win-dhcp-renew", "scn-lan2-verify",
    "win-full-triage", "win-route", "win-ping-loop",
):
    _clue(_lid, lambda f: f["w_ip2"])
_clue("w11-services", lambda f: f["w_svc"])
_clue("w11-processes", lambda f: f["w_proc"])
_clue("w11-wlan", lambda f: "Novak-Staff")
_clue("win-wifi-survey", lambda f: "Novak-Staff")
_clue("hv-vswitch", lambda f: "Lab-Private")
_clue("win-hostname", lambda f: f["w_suffix"])
_clue("w11-inventory", lambda f: f["w_suffix"])
_clue("win-getmac", lambda f: f["w_hop"])


def _gui_enrich(f, seed):
    f["w_ip"] = _seed_ip(seed, 8)
    f["w_ip2"] = _seed_ip(seed, 18)
    f["w_name"] = f"CLINIC-{20 + (seed % 40)}"
    f["w_suffix"] = f"clinic{20 + (seed % 40)}.local"


def _seen(state):
    return ((state.get("gui") or {}).get("seen") or [])


def _gui(lid, checker, syntax, s2p, s3p, s2n, s3n, s2ev, s3ev, ok, after=None, plant=None):
    SK.SPECS[lid] = {
        "syntax": syntax,
        "enrich": _gui_enrich,
        "events": {"assisted": s2ev, "ticket": s3ev},
        "ok": ok,
        "after_guided": after,
        "plant_state": plant,
        "stages": {
            "assisted": {
                "checker": checker, "prose": s2p,
                "note": lambda f, t=s2n: t.format(**f),
                "fix": lambda f: [], "plant": lambda f: [],
                "checks": lambda f: [{"kind": checker, "stage": "assisted"}],
            },
            "ticket": {
                "checker": checker, "prose": s3p,
                "note": lambda f, t=s3n: t.format(**f),
                "fix": lambda f: [], "plant": lambda f: [],
                "checks": lambda f: [{"kind": checker, "stage": "ticket"}],
            },
        },
    }


def _about_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["pane"] = "home"
    gui["seen"] = [e for e in (gui.get("seen") or []) if e not in ("pane:about", "pane:system")]


def _update_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["updates"] = "idle"
    gui["pane"] = "home"
    gui["seen"] = [e for e in (gui.get("seen") or []) if e not in ("pane:update", "update:check")]


def _devices_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["dev_open"] = []
    gui["seen"] = [e for e in (gui.get("seen") or []) if not str(e).startswith("dev:")]


def _renew_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["adapter"] = "down"
    gui["seen"] = [e for e in (gui.get("seen") or []) if not str(e).startswith("adapter:")]


def _ethernet_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["pane"] = "home"
    gui["adapter"] = "up"
    gui["seen"] = [e for e in (gui.get("seen") or []) if e != "pane:ethernet" and not str(e).startswith("adapter:")]


def _accounts_after(state, facts):
    gui = state.setdefault("gui", {})
    gui["pane"] = "home"
    gui["seen"] = [e for e in (gui.get("seen") or []) if e not in ("pane:accounts", "pane:about")]


_gui(
    "gui-about", "about", [("About", "Settings, System, About"), ("System", "Settings, System")],
    "About was open during the walkthrough and is back on the home page. Open About again and read the device name there. Do not type the name into a box.",
    "About is open and System is not. Open System so the display and sound links are on screen. Leaving About open does not finish this.",
    "Open Settings and then About.",
    "Open System. About by itself is the previous stage.",
    lambda f: [{"ev": "pane:about"}],
    lambda f: [{"ev": "pane:system"}],
    lambda state, f, stage: (state.get("gui") or {}).get("pane") == ("about" if stage == "assisted" else "system"),
    _about_after,
)
_gui(
    "gui-ethernet", "ethernet", [("Ethernet", "Settings, Network, Ethernet"), ("Adapter", "Disable, then Enable")],
    "Ethernet properties are not on screen. Open Ethernet and read the IPv4 address, mask, gateway, and DNS. The check is that page, not a typed address.",
    "The Ethernet page is open and the adapter was never cycled. Disable Ethernet, then enable it, from Advanced network settings or Network Connections.",
    "Open the Ethernet page.",
    "Disable the Ethernet adapter, then enable it.",
    lambda f: [{"ev": "pane:ethernet"}],
    lambda f: [{"ev": "adapter:disable"}, {"ev": "adapter:enable"}],
    lambda state, f, stage: ((state.get("gui") or {}).get("pane") == "ethernet") if stage == "assisted"
    else ((state.get("gui") or {}).get("adapter") == "up" and "adapter:disable" in _seen(state)),
    _ethernet_after,
)
_gui(
    "gui-renew", "renew", [("Enable", "Enable the Ethernet adapter"), ("Cycle", "Disable, then Enable")],
    "The Ethernet adapter is disabled, so this desk has no lease. Enable it. The adapter starts down after the walkthrough, so the old enable does not count.",
    "The adapter is up on the lease you just brought back, and it has not been cycled since. Disable it, then enable it again.",
    "Enable the Ethernet adapter.",
    "Disable Ethernet, then enable it.",
    lambda f: [{"ev": "adapter:enable"}],
    lambda f: [{"ev": "adapter:disable"}, {"ev": "adapter:enable"}],
    lambda state, f, stage: ((state.get("gui") or {}).get("adapter") == "up" and "adapter:disable" not in _seen(state)) if stage == "assisted"
    else ((state.get("gui") or {}).get("adapter") == "up" and "adapter:disable" in _seen(state)),
    _renew_after,
)
_gui(
    "gui-services", "service", SVC,
    "Services is open on Defender from the walkthrough. The print spooler has not been selected. Select Print Spooler.",
    "Print Spooler is selected. Windows Update (wuauserv) has not been. Select that service. Spooler staying selected does not pass.",
    "Select the Print Spooler service.",
    "Select the Windows Update service, wuauserv.",
    lambda f: [{"ev": "open:services"}, {"ev": "svc:Spooler"}],
    lambda f: [{"ev": "svc:wuauserv"}],
    lambda state, f, stage: (state.get("gui") or {}).get("svc") == ("Spooler" if stage == "assisted" else "wuauserv"),
)
_gui(
    "gui-update", "updates", [("Windows Update", "Settings, Windows Update"), ("Check", "Check for updates")],
    "Windows Update has not been opened since the walkthrough check was cleared. Open the Windows Update page. Do not click Check for updates yet.",
    "The Windows Update page is open and the last check is still the stale one. Click Check for updates.",
    "Open Windows Update. Do not run the check.",
    "Click Check for updates.",
    lambda f: [{"ev": "pane:update"}],
    lambda f: [{"ev": "update:check"}],
    lambda state, f, stage: ((state.get("gui") or {}).get("pane") == "update" and (state.get("gui") or {}).get("updates") != "checked") if stage == "assisted"
    else (state.get("gui") or {}).get("updates") == "checked",
    _update_after,
)
_gui(
    "gui-accounts", "account", [("Accounts", "Settings, Accounts"), ("About", "Settings, System, About")],
    "Accounts is not on screen. Open Accounts and read the signed-in user before you change anything.",
    "You have the signed-in account. About is closed, so the device name next to that account is not on screen. Open About.",
    "Open Accounts.",
    "Open About and read the device name.",
    lambda f: [{"ev": "pane:accounts"}],
    lambda f: [{"ev": "pane:about"}],
    lambda state, f, stage: (state.get("gui") or {}).get("pane") == ("accounts" if stage == "assisted" else "about"),
    _accounts_after,
)
_gui(
    "gui-devices", "device", [("Network adapters", "Device Manager, Network adapters"), ("Display adapters", "Device Manager, Display adapters")],
    "Device Manager's network adapters are collapsed. Expand Network adapters. Leave Display adapters collapsed.",
    "Network adapters are expanded and Display adapters are not. Expand Display adapters. The network category from practice can stay open.",
    "Expand Network adapters.",
    "Expand Display adapters.",
    lambda f: [{"ev": "open:devmgr"}, {"ev": "dev:net"}],
    lambda f: [{"ev": "dev:display"}],
    lambda state, f, stage: ("net" in ((state.get("gui") or {}).get("dev_open") or []) and "display" not in ((state.get("gui") or {}).get("dev_open") or [])) if stage == "assisted"
    else "display" in ((state.get("gui") or {}).get("dev_open") or []),
    _devices_after,
)


def _plant_ad(state, facts):
    gui = state.get("gui") or {}
    ad = gui.get("ad")
    px = state.setdefault("px", {})
    if not ad or px.get("ad_planted"):
        return
    px["ad_planted"] = True
    ad["users"].append({
        "sam": "ncole", "name": "Nora Cole", "ou": "Sales", "enabled": True, "locked": True,
        "groups": ["Domain Users", "Sales-Staff"], "must_change": False, "pw_reset": False,
    })
    ad["users"].append({
        "sam": "snguyen", "name": "Sam Nguyen", "ou": "HR", "enabled": True, "locked": False,
        "groups": ["Domain Users", "HR-Staff"], "must_change": False, "pw_reset": False,
        "note": "Contractor ended Tuesday",
    })


def _ad_user(state, sam):
    users = ((state.get("gui") or {}).get("ad") or {}).get("users") or []
    return next((u for u in users if u.get("sam") == sam), None)


_gui(
    "win-ad-users", "ad", [("Unlock", "Unlock account"), ("Disable", "Disable account")],
    "Jamie Chen is already unlocked from the walkthrough. Another Sales account is still locked. Unlock that one. It is the locked account that is not jchen.",
    "Nora Cole is unlocked. An HR account is still enabled and its note says the contractor ended. Disable that account. Do not delete it.",
    "Unlock the Sales account that is still locked and is not Jamie Chen.",
    "Disable the HR account whose note says the contractor ended. Do not delete the object.",
    lambda f: [{"ev": "open:aduc"}, {"ev": "ad:unlock", "data": {"sam": "ncole"}}],
    lambda f: [{"ev": "ad:disable", "data": {"sam": "snguyen"}}],
    lambda state, f, stage: (lambda u: bool(u) and not u.get("locked"))(_ad_user(state, "ncole")) if stage == "assisted"
    else (lambda u: bool(u) and not u.get("enabled"))(_ad_user(state, "snguyen")),
    plant=_plant_ad,
)
