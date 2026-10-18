"""Windows simulator fidelity layer: realistic output and real outcomes for wrong attempts; grading unchanged."""
import interactive_labs as IL
import lab_runtime as RT


def run(lab, *cmds):
    st, done, outs = RT.fresh_state(lab), [], []
    for c in cmds:
        r, st, done = IL.run_command(lab, st, done, c)[:3]
        outs.append("\n".join(r["lines"]))
    return outs, done


def test_ipconfig_all_has_every_windows_11_field():
    (o,), _ = run("win-ipconfig", "ipconfig /all")
    for f in ("Primary Dns Suffix", "Node Type . . . . . . . . . . . . : Hybrid", "Physical Address. . . . . . . . . : 00-1A-2B-AA-BB-07",
              "DHCP Enabled. . . . . . . . . . . : Yes", "Link-local IPv6 Address", "IPv4 Address. . . . . . . . . . . : 10.20.30.47(Preferred)",
              "Lease Obtained", "Lease Expires", "DHCP Server", "NetBIOS over Tcpip", "Wireless LAN adapter Wi-Fi:", "Media disconnected"):
        assert f in o, f


def test_release_removes_ipv4_and_a_second_release_fails_like_windows():
    (r1, r2, a), done = run("win-dhcp-renew", "ipconfig /release", "ipconfig /release", "ipconfig /all")
    assert "IPv4 Address" not in r1 and "Default Gateway . . . . . . . . . :" in r1
    assert "no adapter is in the state permissible" in r2
    assert "fec0:0:0:ffff::1%1" in a and "Lease Obtained" not in a
    assert "release" in done


def test_ping_forms():
    (gw, same, far, n2), _ = run("win-dhcp-renew", "ping 10.20.30.1", "ping 10.20.30.99", "ping 8.8.8.8", "ping -n 2 10.20.30.1")
    assert "Approximate round trip times in milli-seconds:" in gw and "Received = 4, Lost = 0" in gw
    assert "Reply from 10.20.30.47: Destination host unreachable." in same and "Received = 4" in same
    assert far.count("Request timed out.") == 4 and "(100% loss)" in far
    assert "Sent = 2, Received = 2" in n2


def test_tracert_agrees_with_ping_and_handles_names():
    (lan, far, bad), _ = run("win-dhcp-renew", "tracert 10.20.30.50", "tracert 8.8.8.8", "tracert nope.example")
    assert "over a maximum of 30 hops:" in lan and "10.20.30.1" not in lan and "Trace complete." in lan
    assert "Request timed out." in far and "Trace complete." not in far
    assert bad.strip() == "Unable to resolve target system name nope.example."


def test_nslookup_specific_and_wrong_server():
    (two, wrong), done = run("win-dhcp-renew", "nslookup gateway.training.local 10.20.30.11", "nslookup gateway.training.local 1.1.1.1")
    assert "Address:  10.20.30.11" in two and "Address:  10.20.30.1" in two
    assert "*** Request to UnKnown timed-out" in wrong


def test_changing_the_adapter_needs_elevation_and_changes_nothing():
    (a, b, c), _ = run("win-dns-break", "netsh interface ip set dns \"Ethernet\" static 1.1.1.1",
                       "Set-DnsClientServerAddress -InterfaceAlias Ethernet -ServerAddresses 1.1.1.1", "ipconfig /all")
    assert "requires elevation" in a and "Access is denied." in b and "FullyQualifiedErrorId" in b
    assert "1.1.1.1" not in c


def test_powershell_error_records():
    (r, s), _ = run("win-dns-break", "Resolve-DnsName nope.training.local", "Get-Service nope")
    assert "At line:1 char:1" in r and "DNS_ERROR_RCODE_NAME_ERROR" in r
    assert "NoServiceFoundForGivenName" in s


def test_grading_is_unchanged():
    ok, _ = RT.verify_all_labs()
    assert ok


def test_wrong_turns_have_real_consequences_and_are_recorded():
    st, done = RT.fresh_state("win-dns-break"), []
    r, st, done = IL.run_command("win-dns-break", st, done, "ipconfig /flushdns")[:3]
    assert "Document first" in "\n".join(r["lines"])
    r, st, done = IL.run_command("win-dns-break", st, done, "ping app.training.local")[:3]
    assert "server-side fix" in "\n".join(r["lines"])
    r, st, done = IL.run_command("win-dns-break", st, done, "ipconfig /release")[:3]
    assert "user is now offline" in "\n".join(r["lines"])
    r, st, done = IL.run_command("win-dns-break", st, done, "ping 10.20.30.50")[:3]
    assert "General failure" in "\n".join(r["lines"]) and "ping_ip_ok" not in done   # really offline
    assert st["wrong_turns"] == ["early_flush", "flush_not_fix", "wrong_release"]
