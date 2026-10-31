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
        f["w_name"] = f"WING-{seed % 90}"
        f["w_suffix"] = f"wing{f['w_ip'].split('.')[1]}.local"

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
        want = "Spooler" if stage == "assisted" else f["w_name"]
        return str(mark.get("service") or "").lower() == want.lower()
    if checker == "renew":
        if stage == "assisted":
            return mark.get("renewed") is True
        return dns == [f["w_ip2"]]
    if checker == "flush":
        if stage == "assisted":
            return dns == [f["w_ip"]]
        return mark.get("flushed") is True and dns == [f["w_ip"]]
    if checker == "wlan":
        want = f["w_name"] if stage == "assisted" else "Novak-Staff"
        return str(mark.get("wlan") or "").lower() == want.lower()
    if checker == "print":
        if stage == "assisted":
            return mark.get("queue") == "clear"
        return mark.get("queue") == "clear" and mark.get("service") == "Spooler"
    if checker == "switch":
        want = f["w_name"] if stage == "assisted" else "Lab-Private"
        return str(mark.get("switch") or "").lower() == want.lower()
    if checker == "arp":
        return mark.get("arp") == ("clear" if stage == "assisted" else "one")
    if checker == "disk":
        return mark.get("disk") == ("1" if stage == "assisted" else "2")
    if checker == "process":
        want = "notepad" if stage == "assisted" else f["w_name"]
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
        want = f["w_name"] if stage == "assisted" else f["w_name"] + "b"
        return str(mark.get("account") or "").lower() == want.lower()
    if checker == "device":
        return "net" in ((state.get("gui") or {}).get("dev_open") or [])
    if checker == "ad":
        return str(mark.get("ad") or "").lower() == f["w_name"].lower()
    if checker == "port":
        return mark.get("port") == ("587" if stage == "assisted" else "25")
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
     "Names for the clinic app still fail, and the address answers. The resolver list on Ethernet is the old pair. The server that holds the record now is the only line in the practice note's incident section.",
     "DNS server for Ethernet: {w_ip}. Leave DHCP in charge of the address.",
     "The app name fails. Use DNS server {w_ip2} on Ethernet.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-net-cli", "dns", WIN,
     "You already showed that a name fails while an address works, using the image resolvers. The practice note names the server that actually has the record. Make that the only DNS server on Ethernet.",
     "The failing name still does not resolve. The DNS server list was never changed. The incident note has the server that should be asked.",
     "Set Ethernet DNS to {w_ip}.",
     "Names still fail. Ethernet should use {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-nslookup-ok", "dns", WIN,
     "The walkthrough lookup used the image DNS servers. Those servers are being retired. The practice note has the replacement. Make it the only server on Ethernet.",
     "Lookups still go to a server that is about to be switched off. The incident note has the replacement address.",
     "Resolver to configure: {w_ip}.",
     "Replace the resolver with {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-ipconfig", "dns", WIN,
     "The full address listing on this PC still shows the image DNS servers, and the charting name will not resolve. The practice note has the server this adapter should use. Set that and leave the address on automatic.",
     "The identity you recorded is stale because the resolver changed this morning. The incident note has the DNS server Ethernet should use now.",
     "Ethernet DNS: {w_ip}.",
     "Update Ethernet DNS to {w_ip2}. The address stays on DHCP.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("w11-powershell-net", "dns", WIN,
     "The address view from the shell showed the image DNS servers. The practice note has the server the branch file share was moved to. Set that on Ethernet.",
     "The branch share still fails by name. The resolver list was not updated. The incident note has the server.",
     "Set the Ethernet resolver to {w_ip}.",
     "The share's resolver is {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("w11-netsh", "dns", WIN,
     "Both address tools showed the image DNS servers. The practice note has the server this site published. Set it with the DNS cmdlet. Leave the address on DHCP.",
     "The older interface tool and ipconfig still disagree with the site's resolver. The incident note has the address Ethernet should use.",
     "DNS server: {w_ip}.",
     "Point Ethernet at {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("gui-ethernet", "dns", WIN,
     "Ethernet properties still list the image DNS servers. The practice note has the resolver for this moved desk. Set that server. Leave the address automatic.",
     "The desk was moved again and the resolver in Ethernet properties is the practice one, which this wing does not use. The incident note has the server to use now.",
     "In Ethernet, set DNS to {w_ip}.",
     "Ethernet DNS should be {w_ip2}.",
     lambda f: f["w_ip"], lambda f: f["w_ip2"], lambda f: {}, _dns_match)

_reg("scn-dns-evidence", "dns", WIN,
     "The third-floor caller can open the proxy by address and nothing by name. This PC is the evidence station. The practice note has the DNS server that should hold the intranet record. Point Ethernet at it.",
     "The name still fails after the first change. The incident note has the resolver the floor should be using now.",
     "Evidence PC DNS: {w_ip}.",
     "The floor resolver is {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-flushdns", "flush", WIN,
     "You cleared the cache and it filled again from the same retired server. The practice note has the server to configure, and the cache has to be cleared after that change or the old answer sticks.",
     "The name fails again. The cache was flushed and the server list was not changed, or the other way around. The incident note has the server. Set it, then flush.",
     "Set DNS to {w_ip}, then flush the cache.",
     "Set DNS to {w_ip} and flush. The old cache entry is not the fix by itself.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: "ipconfig /flushdns",
     lambda f: {"flushed": False}, _flush_match)

# flush stage 3 only sets flushed, but _ok for flush requires dns == w_ip AND flushed.
# Stage 3 command is only flush. Stage 2 sets dns. If both must be true at stage 3, stage 2's dns must remain.
# Stage 3 check uses w_ip not w_ip2. Good if stage 2 already set dns. Plant doesn't clear dns.
# Stage 3 fix is only flush. Student must have set DNS in stage 2. Solver runs stage 2 first. Good.

_reg("win-dhcp-renew", "renew", WIN,
     "Cycling the lease brought back the image DNS servers. The practice note has the resolver this lease should keep. Renew, and set that DNS server.",
     "The laptop still holds Friday's resolver after the LAN came back. Renew the lease and set the DNS server in the incident note.",
     "Renew the lease and set DNS to {w_ip}.",
     "Renew, then set DNS to {w_ip2}.",
     lambda f: "ipconfig /renew",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {"renewed": False}, _renew_match)

_reg("scn-lan2-verify", "renew", WIN,
     "The CFO laptop still has Friday's resolver. Renew the lease and set the DNS server in the practice note.",
     "The laptop got a new lease and is still asking the old resolver. The incident note has the server.",
     "Renew the lease.",
     "After the renew, DNS should be {w_ip2}.",
     lambda f: "ipconfig /renew",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {"renewed": False}, _renew_match)

_reg("win-full-triage", "dns", WIN,
     "The full triage used the image DNS pair. This desk moved to a wing whose resolver is in the practice note. Set that server. Keep the address on DHCP.",
     "Lookups still use the wing you moved away from. The incident note has the resolver for the wing this PC is in now.",
     "Wing resolver: {w_ip}.",
     "This wing's resolver is {w_ip2}.",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip']}",
     lambda f: f"Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses {f['w_ip2']}",
     lambda f: {}, _dns_match)

_reg("win-route", "route", ROUTE,
     "The route table shows a default gateway that no longer forwards. The practice note has the next hop to install for 0.0.0.0. Add that route. Do not delete the connected subnet.",
     "Traffic off the subnet dies on this PC. The default route is missing or points at the old hop. The incident note has the gateway to add.",
     "Add a default route via {w_hop}.",
     "The default gateway to add is {w_ip2}.",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_hop']}",
     lambda f: f"route add 0.0.0.0 mask 0.0.0.0 {f['w_ip2']}",
     lambda f: {"hop": ""}, _route_match)

_reg("win-ping-loop", "route", ROUTE,
     "Loopback answers, so the stack is up. Anything past the local subnet does not, because there is no default route. The practice note has the hop.",
     "Ping to the gateway times out and loopback still answers. The incident note has the hop that should be the default route.",
     "Default hop: {w_hop}.",
     "Install a default route via {w_ip2}.",
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
     "A different service, named in the incident note, is stopped. Start that one. Do not stop Defender.",
     "Start the Spooler service.",
     "Start the service named {w_name}.",
     lambda f: "Start-Service Spooler",
     lambda f: f"Start-Service {f['w_name']}",
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
     "The laptop fell back to a guest network. The incident note has the profile it should be on.",
     "Connect to {w_name}.",
     "Connect to Novak-Staff.",
     lambda f: f"netsh wlan connect name={f['w_name']}",
     lambda f: "netsh wlan connect name=Novak-Staff",
     lambda f: {"wlan": ""}, _wlan_match)

_reg("win-wifi-survey", "wlan", WLAN,
     "The survey shows the laptop associated to a neighboring office. The practice note has the profile this building uses.",
     "After the survey the laptop is on the guest SSID again. Connect it to the staff profile.",
     "Join {w_name}.",
     "Join Novak-Staff.",
     lambda f: f"netsh wlan connect name={f['w_name']}",
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
     "Another process, named in the incident note, is stuck. Stop that one.",
     "Stop notepad.",
     "Stop {w_name}.",
     lambda f: "Stop-Process -Name notepad",
     lambda f: f"Stop-Process -Name {f['w_name']}",
     lambda f: {"killed": ""}, _proc_match)

_reg("hv-vswitch", "switch", [("List switches", "Get-VMSwitch"), ("Create one", "New-VMSwitch -Name <name> -SwitchType Private")],
     "The lab guests are still on the default switch. The practice note has the private switch to create.",
     "The private switch from practice is not the one the change record names. Create the switch in the incident note.",
     "Create a private switch named {w_name}.",
     "Create private switch Lab-Private.",
     lambda f: f"New-VMSwitch -Name {f['w_name']} -SwitchType Private",
     lambda f: "New-VMSwitch -Name Lab-Private -SwitchType Private",
     lambda f: {"switch": ""}, _switch_match)

_reg("win-getmac", "adapter", [("Show the MAC", "getmac"), ("Enable the adapter", "netsh interface set interface Ethernet enable")],
     "getmac shows Ethernet as media disconnected because the adapter is disabled. Enable it. The MAC does not change.",
     "Ethernet is disabled again, so the MAC the asset system wants is not on the wire. Enable the adapter.",
     "Enable Ethernet.",
     "The adapter is down. Enable Ethernet.",
     lambda f: "netsh interface set interface Ethernet enable",
     lambda f: "netsh interface set interface Ethernet enable",
     lambda f: {"adapter": "down"}, _adapter_match)

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
     "Inventory merged this PC with another image. The incident note has the name and the suffix this PC should use.",
     "Name: {w_name}. Suffix: wing{w_ip}.",
     "Set the name to {w_name} and the suffix from the note.",
     lambda f: f"Rename-Computer -NewName {f['w_name']}",
     lambda f: f"netsh interface ip set dnsSuffix {f['w_suffix']}",
     lambda f: {"suffix": ""}, _id_match)

# identity check needs BOTH hostname and suffix. Stage 2 only renames. Stage 3 only sets suffix.
# _ok requires both. Stage 2 fails until both exist. Solver runs stage 2 then 3, but stage 2 observe happens before stage 3.
# Stage 2 won't latch. I need _ok for identity: assisted checks hostname, ticket checks both.

_reg("w11-inventory", "identity", WIN,
     "The inventory still shows the image name and an empty DNS suffix. The practice note has the name. Set it. The suffix is stage 3.",
     "The name is updated and the suffix is still empty, so the inventory row does not match the domain. Set the suffix from the incident note.",
     "Set the computer name to {w_name}.",
     "Set the DNS suffix to {w_suffix}.",
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

_reg("win-netstat", "port", [("Connections", "netstat -ano"), ("Test a port", "Test-NetConnection <host> -Port <port>")],
     "netstat shows nothing listening on the mail submission port. Confirm port 587 answers. The practice note has the host.",
     "Mail is failing on the other port. Confirm port 25. Do not open 587 to the world.",
     "Test port 587.",
     "Test port 25.",
     lambda f: "Test-NetConnection mail.novak.local -Port 587",
     lambda f: "Test-NetConnection mail.novak.local -Port 25",
     lambda f: {"port": ""}, _port_match)

_reg("win-laptop-ports", "port", [("Port test", "Test-NetConnection <host> -Port <port>")],
     "The laptop can resolve mail and cannot connect. The practice note says to prove port 587.",
     "Submission works and the relay on port 25 does not. Prove port 25.",
     "Test 587.",
     "Test 25.",
     lambda f: "Test-NetConnection mail.novak.local -Port 587",
     lambda f: "Test-NetConnection mail.novak.local -Port 25",
     lambda f: {"port": ""}, _port_match)
