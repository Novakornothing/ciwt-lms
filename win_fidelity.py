"""Windows simulator fidelity layer (round 2).

The command engine in interactive_labs.run_windows decides what a command *does* (state changes, objectives).
This layer only decides what Windows would *print*, from the same state, so grading is unchanged:
  * ipconfig / ipconfig /all with every field Windows 11 shows (DNS suffix, link-local IPv6, lease times,
    DHCP server, a disconnected Wi-Fi adapter), the real post-/release form and APIPA addresses
  * ping with real statistics and RTT summary, -n, and the real "Destination host unreachable" reply from
    your own address when a host on your subnet does not answer ARP (it counts as Received!)
  * nslookup NAME SERVER (asking a specific or wrong server), Non-authoritative answers for outside names
  * tracert with the header, one hop on the local subnet, timeouts after the gateway, unresolvable names
  * PowerShell: Resolve-DnsName / Test-Connection / Get-Service tables and full error records
  * real outcomes for attempts the simulator used to reject: netsh/Set-DnsClientServerAddress changes need
    elevation (the trainee is a standard user), ipconfig /release twice, getmac, arp -a, route print
It is still a simulation: nothing here touches a real network, and the lab page says so.
"""
import ipaddress
import random
import re
from datetime import datetime, timedelta

ETH_DESC = "Intel(R) Ethernet Connection (17) I219-LM"
WIFI_DESC = "Intel(R) Wi-Fi 6E AX211 160MHz"
ETH_MAC = "00-1A-2B-AA-BB-07"
WIFI_MAC = "3C-21-9C-5E-7A-10"
LL6 = "fe80::4c1d:9a2e:7b31:a8f2%12"
SVC_NAMES = {"dhcp": "DHCP Client", "dnscache": "DNS Client", "windefend": "Microsoft Defender Antivirus Service",
             "wuauserv": "Windows Update", "spooler": "Print Spooler", "lanmanworkstation": "Workstation",
             "lanmanserver": "Server", "mpssvc": "Windows Defender Firewall", "w32time": "Windows Time",
             "bits": "Background Intelligent Transfer Service", "eventlog": "Windows Event Log", "netlogon": "Netlogon",
             "termservice": "Remote Desktop Services", "winrm": "Windows Remote Management (WS-Management)"}


def _suffix(st):
    return (st.get("dns_suffix") or (str(st.get("domain") or "training").lower() + ".local")).lower()


_LBL = {  # the exact strings Windows 11 prints (label + dot leaders), so they line up like the real thing
    "host": "   Host Name . . . . . . . . . . . . :", "pdns": "   Primary Dns Suffix  . . . . . . . :",
    "node": "   Node Type . . . . . . . . . . . . :", "iprt": "   IP Routing Enabled. . . . . . . . :",
    "wins": "   WINS Proxy Enabled. . . . . . . . :", "srch": "   DNS Suffix Search List. . . . . . :",
    "media": "   Media State . . . . . . . . . . . :", "csfx": "   Connection-specific DNS Suffix  . :",
    "desc": "   Description . . . . . . . . . . . :", "mac": "   Physical Address. . . . . . . . . :",
    "dhcp": "   DHCP Enabled. . . . . . . . . . . :", "auto": "   Autoconfiguration Enabled . . . . :",
    "ll6": "   Link-local IPv6 Address . . . . . :", "ip4": "   IPv4 Address. . . . . . . . . . . :",
    "apipa": "   Autoconfiguration IPv4 Address. . :", "mask": "   Subnet Mask . . . . . . . . . . . :",
    "lo": "   Lease Obtained. . . . . . . . . . :", "le": "   Lease Expires . . . . . . . . . . :",
    "gw": "   Default Gateway . . . . . . . . . :", "dsrv": "   DHCP Server . . . . . . . . . . . :",
    "iaid": "   DHCPv6 IAID . . . . . . . . . . . :", "duid": "   DHCPv6 Client DUID. . . . . . . . :",
    "dns": "   DNS Servers . . . . . . . . . . . :", "nbt": "   NetBIOS over Tcpip. . . . . . . . :",
}
_CONT = " " * 39


def _when(dt):
    return f"{dt:%A}, {dt:%B} {dt.day}, {dt:%Y} {dt.hour % 12 or 12}:{dt:%M:%S} {'AM' if dt.hour < 12 else 'PM'}"


def _lease(st):
    if not st.get("lease_at"):
        st["lease_at"] = (datetime.now() - timedelta(hours=1, minutes=17)).replace(microsecond=0).isoformat()
    t = datetime.fromisoformat(st["lease_at"])
    return t, t + timedelta(days=8)


def ipconfig(st, full):
    rel = bool(st.get("released"))
    ip = st.get("ipv4") or ""
    apipa = ip.startswith("169.254.")
    dhcp = bool(st.get("dhcp", True))
    sfx = "" if rel else _suffix(st)
    out = ["", "Windows IP Configuration", ""]
    if full:
        out += [f"{_LBL['host']} {st.get('hostname', 'PC')}", f"{_LBL['pdns']} {_suffix(st)}", f"{_LBL['node']} Hybrid",
                f"{_LBL['iprt']} No", f"{_LBL['wins']} No", f"{_LBL['srch']} {_suffix(st)}", ""]
    else:
        out.append("")
    out += ["Ethernet adapter Ethernet:", "", f"{_LBL['csfx']} {sfx}".rstrip()]
    if full:
        out += [f"{_LBL['desc']} {ETH_DESC}", f"{_LBL['mac']} {st.get('mac') or ETH_MAC}",
                f"{_LBL['dhcp']} {'Yes' if dhcp else 'No'}", f"{_LBL['auto']} Yes"]
    pref = "(Preferred)" if full else ""
    out.append(f"{_LBL['ll6']} {LL6}{pref}")
    if not rel and ip and ip != "0.0.0.0":
        out.append(f"{_LBL['apipa' if apipa else 'ip4']} {ip}{pref}")
        out.append(f"{_LBL['mask']} {'255.255.0.0' if apipa else st.get('mask')}")
        if full and dhcp and not apipa:
            lo, le = _lease(st)
            out += [f"{_LBL['lo']} {_when(lo)}", f"{_LBL['le']} {_when(le)}"]
    gw = "" if rel or apipa else (st.get("gateway") or "")
    out.append(f"{_LBL['gw']} {gw}".rstrip())
    if full:
        if dhcp and not rel and not apipa:
            out.append(f"{_LBL['dsrv']} {st.get('dhcp_server') or (st.get('dns') or [st.get('gateway')])[0]}")
        out += [f"{_LBL['iaid']} 100668059", f"{_LBL['duid']} 00-01-00-01-2E-6A-1B-33-{(st.get('mac') or ETH_MAC)}"]
        dns = ["fec0:0:0:ffff::1%1", "fec0:0:0:ffff::2%1", "fec0:0:0:ffff::3%1"] if rel or apipa else list(st.get("dns") or [])
        for i, d in enumerate(dns):
            out.append(f"{_LBL['dns']} {d}" if i == 0 else _CONT + d)
        out.append(f"{_LBL['nbt']} Enabled")
    out += ["", "Wireless LAN adapter Wi-Fi:", "", f"{_LBL['media']} Media disconnected", _LBL["csfx"]]
    if full:
        out += [f"{_LBL['desc']} {WIFI_DESC}", f"{_LBL['mac']} {WIFI_MAC}", f"{_LBL['dhcp']} Yes", f"{_LBL['auto']} Yes"]
    return out


def _same_subnet(st, target):
    try:
        net = ipaddress.ip_network(f"{st.get('ipv4')}/{st.get('mask') or '255.255.255.0'}", strict=False)
        return ipaddress.ip_address(target) in net
    except ValueError:
        return False


def _rng(st, key):
    return random.Random(f"{st.get('hostname')}:{key}:{st.get('_fid_n', 0)}")


def _count(c):
    m = re.search(r"\s-n\s+(\d+)", c)
    return max(1, min(int(m.group(1)), 10)) if m else 4


def ping(c, st, lines):
    """Re-render a ping the engine already decided (reply / timeout / name failure) in exact Windows form."""
    joined = "\n".join(lines)
    if not lines or not lines[0].startswith("Pinging"):
        return None
    n = _count(c)
    if "General failure" in joined:      # no IPv4 address (after /release): Windows' exact form, plus the engine's coaching note
        note = [ln for ln in lines if ln.startswith("(")]
        tgt = lines[0].split()[1]
        return ["", lines[0]] + ["PING: transmit failed. General failure."] * n + \
            ["", f"Ping statistics for {tgt}:", f"    Packets: Sent = {n}, Received = 0, Lost = {n} (100% loss),", ""] + note
    m = re.match(r"Pinging (\S+)(?: \[([\d.]+)\])? with", lines[0])
    if not m:
        return None
    name, ip = m.group(1), m.group(2) or m.group(1)
    head = f"Pinging {name} [{ip}] with 32 bytes of data:" if m.group(2) else f"Pinging {ip} with 32 bytes of data:"
    rep = [ln for ln in lines if ln.startswith("Reply from")]
    out = ["", head]
    r = _rng(st, ip)
    if rep and "unreachable" not in rep[0]:
        ttl = re.search(r"TTL=(\d+)", rep[0])
        ttl = ttl.group(1) if ttl else "64"
        tm = re.search(r"time[=<](\d+)ms", rep[0])
        base = int(tm.group(1)) if tm else 0
        times = [max(0, base + r.choice([0, 0, 0, 1])) for _ in range(n)]
        for t in times:
            out.append(f"Reply from {ip}: bytes=32 time{'<1' if t == 0 else '=' + str(t)}ms TTL={ttl}")
        out += ["", f"Ping statistics for {ip}:", f"    Packets: Sent = {n}, Received = {n}, Lost = 0 (0% loss),",
                "Approximate round trip times in milli-seconds:",
                f"    Minimum = {min(times)}ms, Maximum = {max(times)}ms, Average = {round(sum(times) / n)}ms"]
        return out
    if _same_subnet(st, ip) and ip != st.get("ipv4"):
        # nobody answered ARP: Windows answers itself, and counts the replies as received
        out += [f"Reply from {st.get('ipv4')}: Destination host unreachable."] * n
        out += ["", f"Ping statistics for {ip}:", f"    Packets: Sent = {n}, Received = {n}, Lost = 0 (0% loss),"]
        return out
    out += ["Request timed out."] * n
    out += ["", f"Ping statistics for {ip}:", f"    Packets: Sent = {n}, Received = 0, Lost = {n} (100% loss),"]
    return out


def tracert(c, st, lines):
    if st.get("ext_hosts") is not None or not lines or not lines[0].startswith("Tracing route"):
        return None
    target = c.split()[-1]
    nm = {k.lower(): v for k, v in (st.get("name_map") or {}).items()}
    ip = target
    if any(ch.isalpha() for ch in target):
        ip = nm.get(target.lower())
        if not ip:
            return [f"Unable to resolve target system name {target}."]
    head = f"Tracing route to {target} [{ip}]" if ip != target else f"Tracing route to {ip}"
    out = ["", head, "over a maximum of 30 hops:", ""]
    if st.get("released"):
        return out[:-1] + ["", "Transmit error: code 1231.", "", "Trace complete."]
    # the same reachability ping uses, so tracert and ping never disagree
    reach = ip in (st.get("pingable_ips") or []) or ip in (st.get("gateway"), st.get("ipv4")) or ip in nm.values()
    if _same_subnet(st, ip):
        out.append(f"  1    <1 ms    <1 ms    <1 ms  {ip}" if reach else "  1     *        *        *     Request timed out.")
        if not reach:
            out += [f"  2     *        *        *     Request timed out.", "  …    (tracert keeps trying to hop 30 — Ctrl+C stops it; the simulator stops here)"]
            return out
        return out + ["", "Trace complete."]
    out.append(f"  1    <1 ms    <1 ms    <1 ms  {st.get('gateway')}")
    if reach:
        out.append(f"  2     1 ms     1 ms    <1 ms  {ip}")
        return out + ["", "Trace complete."]
    for h in (2, 3, 4):
        out.append(f"  {h}     *        *        *     Request timed out.")
    out.append("  …    (tracert keeps trying to hop 30 — Ctrl+C stops it; the simulator stops here)")
    return out


def _ps_error(cmd, msg, cat, fqid):
    return [f"{cmd.split()[0]} : {msg}", "At line:1 char:1", f"+ {cmd}", "+ " + "~" * min(len(cmd), 60),
            f"    + CategoryInfo          : {cat}", f"    + FullyQualifiedErrorId : {fqid}", ""]


def resolve_dnsname(c, st, lines):
    if not lines:
        return None
    name = c.split(None, 1)[1].split()[0] if len(c.split()) > 1 else ""
    if lines[0].startswith("Resolve-DnsName :"):
        return _ps_error(c, f"{name} : DNS name does not exist",
                         f"ResourceUnavailable: ({name}:String) [Resolve-DnsName], Win32Exception",
                         "DNS_ERROR_RCODE_NAME_ERROR,Microsoft.DnsClient.Commands.ResolveDnsName")
    m = re.search(r"(\d+\.\d+\.\d+\.\d+)\s*$", lines[-1])
    if not m:
        return None
    w = max(len(name) + 2, 47)
    return ["", f"{'Name':<{w}}Type   TTL   Section    IPAddress", f"{'----':<{w}}----   ---   -------    ---------",
            f"{name:<{w}}A      1200  Answer     {m.group(1)}", ""]


def test_connection(c, st, lines):
    if not lines:
        return None
    target = c.split()[-1]
    if lines[0].startswith("Testing"):
        return _ps_error(c, f"Testing connection to computer '{target}' failed: Error due to lack of resources",
                         f"ResourceUnavailable: ({target}:String) [Test-Connection], PingException",
                         "TestConnectionException,Microsoft.PowerShell.Commands.TestConnectionCommand")
    n = _count(c.replace("-Count", "-n").replace("-count", "-n"))
    host = st.get("hostname", "PC")
    out = ["", "Source        Destination     IPV4Address      IPV6Address                              Bytes    Time(ms)",
           "------        -----------     -----------      -----------                              -----    --------"]
    for _ in range(n):
        out.append(f"{host:<14}{target:<16}{target:<17}{'':<41}{'32':<9}{_rng(st, target).choice([0, 0, 1])}")
    return out + [""]


def get_service(c, st, lines):
    if not lines:
        return None
    if lines[0].startswith("Get-Service :"):
        nm = re.search(r"'([^']+)'", lines[0])
        nm = nm.group(1) if nm else "?"
        return _ps_error(c, f"Cannot find any service with service name '{nm}'.",
                         f"ObjectNotFound: ({nm}:String) [Get-Service], ServiceCommandException",
                         "NoServiceFoundForGivenName,Microsoft.PowerShell.Commands.GetServiceCommand")
    rows = [ln.split() for ln in lines[2:] if ln.strip()]
    out = ["", "Status   Name               DisplayName", "------   ----               -----------"]
    for r in rows:
        if len(r) >= 2:
            out.append(f"{r[0]:<9}{r[1]:<19}{SVC_NAMES.get(r[1].lower(), r[1])}")
    return out + [""]


def getmac(st):
    return ["", "Physical Address    Transport Name", "=================== ==========================================================",
            f"{st.get('mac') or ETH_MAC}   " + ("Media disconnected" if st.get("released") and False else r"\Device\Tcpip_{6F1C2A3B-8D4E-4F50-9A61-B2C3D4E5F607}"),
            f"{WIFI_MAC}   Media disconnected"]


def arp(st):
    gw = st.get("gateway") or "10.20.30.1"
    pre = ".".join((st.get("ipv4") or "10.20.30.47").split(".")[:3])
    return ["", f"Interface: {st.get('ipv4')} --- 0xc", "  Internet Address      Physical Address      Type",
            f"  {gw:<22}00-1a-2b-3c-4d-01     dynamic", f"  {pre + '.255':<22}ff-ff-ff-ff-ff-ff     static",
            f"  {'224.0.0.22':<22}01-00-5e-00-00-16     static", f"  {'224.0.0.251':<22}01-00-5e-00-00-fb     static",
            f"  {'239.255.255.250':<22}01-00-5e-7f-ff-fa     static", f"  {'255.255.255.255':<22}ff-ff-ff-ff-ff-ff     static"]


def route_print(st):
    ip, gw = st.get("ipv4"), st.get("gateway")
    pre = ".".join((ip or "10.20.30.47").split(".")[:3])
    rows = [("0.0.0.0", "0.0.0.0", gw, ip, "25"), ("127.0.0.0", "255.0.0.0", "On-link", "127.0.0.1", "331"),
            ("127.0.0.1", "255.255.255.255", "On-link", "127.0.0.1", "331"), (pre + ".0", st.get("mask"), "On-link", ip, "281"),
            (ip, "255.255.255.255", "On-link", ip, "281"), (pre + ".255", "255.255.255.255", "On-link", ip, "281"),
            ("224.0.0.0", "240.0.0.0", "On-link", ip, "281"), ("255.255.255.255", "255.255.255.255", "On-link", ip, "281")]
    if st.get("released") or not gw:
        rows = rows[1:3] + rows[6:]
    out = ["===========================================================================", "Interface List",
           f" 12...{(st.get('mac') or ETH_MAC).lower().replace('-', ' ')} ......{ETH_DESC}",
           f" 14...{WIFI_MAC.lower().replace('-', ' ')} ......{WIFI_DESC}",
           "  1...........................Software Loopback Interface 1",
           "===========================================================================", "", "IPv4 Route Table",
           "===========================================================================", "Active Routes:",
           "Network Destination        Netmask          Gateway       Interface  Metric"]
    for d, m, g, i, me in rows:
        out.append(f"{d:>19}{m:>17}{g:>17}{i:>16}{me:>7}")
    return out + ["===========================================================================", "Persistent Routes:", "  None"]


_SET_DNS = re.compile(r"^(netsh\s+(interface|int)\s+(ip|ipv4)\s+(set|add)\s+(dns|dnsservers?)\b|set-dnsclientserveraddress\b|"
                      r"netsh\s+(interface|int)\s+(ip|ipv4)\s+set\s+(address|addr)\b|new-netipaddress\b|set-netipinterface\b)", re.I)


def elevation(c, st):
    """Changing adapter settings needs an elevated prompt; the trainee is a standard user (as on a managed PC)."""
    if not _SET_DNS.match(c):
        return None
    if c.lower().startswith(("set-dnsclientserveraddress", "new-netipaddress", "set-netipinterface")):
        verb = c.split()[0]
        out = _ps_error(c, "Access is denied.", f"PermissionDenied: (MSFT_DNSClientServerAddress:ROOT/StandardCimv2/...) [{verb}], CimException",
                        f"Windows System Error 5,{verb}")
    else:
        out = ["The requested operation requires elevation (Run as administrator)."]
    return out + ["(Simulation: you are signed in as a standard user, as on a managed help-desk PC. Changing the adapter is "
                  "not the fix this ticket needs — find where the fault really is first.)"]


def nslookup_server(c, st):
    """nslookup NAME SERVER — returns (rewritten command for the engine, server) or (None, output)."""
    parts = c.split()
    if len(parts) != 3 or st.get("dns_primary_down") is not None:
        return None
    name, server = parts[1], parts[2]
    if server in (st.get("dns") or []):
        return ("nslookup " + name, server)
    try:
        ipaddress.ip_address(server)
    except ValueError:
        return None
    return (None, ["DNS request timed out.", "    timeout was 2 seconds.", "Server:  UnKnown", f"Address:  {server}", "",
                   "DNS request timed out.", "    timeout was 2 seconds.", "DNS request timed out.", "    timeout was 2 seconds.",
                   f"*** Request to UnKnown timed-out"])


def nslookup(c, st, lines, server=None):
    if not lines or not lines[0].startswith("Server:"):
        return None
    out = list(lines)
    if server:
        out[1] = f"Address:  {server}"
        if server != (st.get("dns") or [None])[0]:
            out[0] = "Server:  UnKnown"
    name = c.split()[1] if len(c.split()) > 1 else ""
    if any(ln.startswith("Name:") for ln in out) and "." in name and not name.lower().endswith(_suffix(st)):
        i = next(i for i, ln in enumerate(out) if ln.startswith("Name:"))
        out.insert(i, "Non-authoritative answer:")
    return out


def wrong_turns(cl, before, st, done, lines):
    """Branching on a wrong hypothesis: the engine already applied the real consequence (e.g. /release really takes the
    user offline); this adds what a senior tech would point out, and records it so scenario mode can report it."""
    objs = st.get("objectives") or []
    dns_ticket = "nslookup_fail" in objs
    note = None
    if cl == "ipconfig /release" and dns_ticket and "release" not in objs and not before.get("released"):
        note = ("wrong_release", "(Ticket impact: the user is now offline. The evidence points at name resolution, and /release "
                "does not touch DNS. Restore service with ipconfig /renew and record what happened.)")
    elif cl == "ipconfig /flushdns" and dns_ticket and "nslookup_fail" not in done:
        note = ("early_flush", "(Flushing before you have evidence throws away what was cached. Document first: nslookup the name, "
                "then flush.)")
    elif cl.startswith("ping ") and dns_ticket and before.get("dns_cache_flushed") and any("could not find host" in ln for ln in lines):
        note = ("flush_not_fix", "(Still failing after /flushdns, so the client cache was not the problem: the DNS server has no "
                "record for this name. That is a server-side fix — escalate with your nslookup output.)")
    if note:
        wt = st.setdefault("wrong_turns", [])
        if note[0] not in wt:
            wt.append(note[0])
        return lines + ["", note[1]]
    return lines
