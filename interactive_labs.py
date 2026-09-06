"""
CIWT Interactive Lab Engine — progressive CLI simulators.
Windows → Switch → Router skills build across labs; later labs reuse earlier commands.
"""

from copy import deepcopy


def _lab(id, title, kind, blurb, objectives, intro, success_msg, initial_state, hints=None, builds_on=None):
    return {
        "id": id,
        "title": title,
        "kind": kind,
        "blurb": blurb,
        "objectives": objectives,
        "intro": intro,
        "success_msg": success_msg,
        "initial_state": initial_state,
        "hints": hints or [],
        "builds_on": builds_on or [],
    }


def _win_state(**extra):
    base = {
        "hostname": "CIWT-W11-07",
        "ipv4": "10.20.30.47",
        "mask": "255.255.255.0",
        "gateway": "10.20.30.1",
        "dns": ["10.20.30.10", "10.20.30.11"],
        "dhcp": True,
        "released": False,
        "dns_cache_flushed": False,
        "shell": "cmd",
        "edition": "Windows 11 Education",
        "version": "23H2",
        "build": "22631.3737",
        "user": "CIWT\\Trainee",
        "domain": "TRAINING",
        "pingable_ips": ["127.0.0.1", "10.20.30.1", "10.20.30.47", "10.20.30.50"],
        "name_map": {"gateway.training.local": "10.20.30.1"},
        "services": {
            "Dhcp": "Running",
            "Dnscache": "Running",
            "WinDefend": "Running",
            "wuauserv": "Running",
            "Spooler": "Running",
        },
        "users": ["Trainee", "Administrator"],
    }
    base.update(extra)
    return base


def _sw_state(**extra):
    base = {
        "hostname": "SW-ACCESS-01",
        "mode": "user",
        "prompt_if": None,
        "edit_vlan": None,
        "vlans": {1: "default"},
        "interfaces": {
            "FastEthernet0/1": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
            "FastEthernet0/2": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
            "FastEthernet0/3": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
        },
    }
    base.update(extra)
    return base


def _rtr_state(**extra):
    base = {
        "hostname": "R1",
        "mode": "user",
        "prompt_if": None,
        "interfaces": {
            "GigabitEthernet0/0": {"ip": None, "mask": None, "up": False, "admin": False},
            "GigabitEthernet0/1": {"ip": None, "mask": None, "up": False, "admin": False},
        },
        "hosts": {"10.20.0.10": True, "10.30.0.20": True},
    }
    base.update(extra)
    return base


LABS = [
    # ── Windows foundation ──────────────────────────────────────────
    _lab(
        "win-ipconfig",
        "1. Windows 11 VM — Read Network Identity",
        "windows",
        "hostname + ipconfig /all — baseline ticket evidence.",
        [
            {"id": "run_hostname", "text": "Run hostname"},
            {"id": "run_ipconfig", "text": "Run ipconfig /all"},
        ],
        "Discover who this PC is on the network. Every help-desk ticket starts here.",
        "You can pull hostname, IPv4, gateway, and DNS from CLI.",
        _win_state(),
        hints=["hostname", "ipconfig /all"],
    ),
    _lab(
        "win-dns-break",
        "2. Windows 11 VM — DNS Failure Isolation",
        "windows",
        "Reuse ping + ipconfig skills; prove name resolution is the fault.",
        [
            {"id": "run_ipconfig", "text": "Document current config with ipconfig /all"},
            {"id": "ping_ip_ok", "text": "Ping 10.20.30.50 (IP works)"},
            {"id": "ping_name_fail", "text": "Ping app.training.local (name fails)"},
            {"id": "nslookup_fail", "text": "nslookup app.training.local"},
            {"id": "flush_dns", "text": "ipconfig /flushdns"},
        ],
        "Browser opens by IP but not by name. Use the identity skills from Lab 1, then isolate DNS.",
        "You proved reachability by IP and failure by name — classic DNS-path evidence.",
        _win_state(name_map={}, dns=["10.20.30.10"]),
        hints=["ipconfig /all", "ping 10.20.30.50", "ping app.training.local", "nslookup app.training.local", "ipconfig /flushdns"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "win-dhcp-renew",
        "3. Windows 11 VM — DHCP Release / Renew",
        "windows",
        "Reuse ipconfig; practice lease cycle and re-check connectivity.",
        [
            {"id": "run_ipconfig", "text": "ipconfig /all before changes"},
            {"id": "release", "text": "ipconfig /release"},
            {"id": "renew", "text": "ipconfig /renew"},
            {"id": "ping_gw", "text": "Ping the gateway to confirm connectivity"},
        ],
        "Lease looks stale. Document → release → renew → verify gateway with ping (Lab 1–2 skills).",
        "You can safely cycle a DHCP lease and prove the gateway still answers.",
        _win_state(),
        hints=["ipconfig /all", "ipconfig /release", "ipconfig /renew", "ping 10.20.30.1"],
        builds_on=["win-ipconfig", "win-dns-break"],
    ),
    _lab(
        "win-full-triage",
        "4. Windows 11 VM — Full Client Triage",
        "windows",
        "Combine identity, DNS, DHCP, and ping into one ticket workflow.",
        [
            {"id": "run_hostname", "text": "hostname"},
            {"id": "run_ipconfig", "text": "ipconfig /all"},
            {"id": "ping_ip_ok", "text": "ping 10.20.30.50"},
            {"id": "ping_name_fail", "text": "ping app.training.local"},
            {"id": "nslookup_fail", "text": "nslookup app.training.local"},
            {"id": "flush_dns", "text": "ipconfig /flushdns"},
            {"id": "release", "text": "ipconfig /release"},
            {"id": "renew", "text": "ipconfig /renew"},
            {"id": "ping_gw", "text": "ping gateway after renew"},
        ],
        "Full ticket: document PC identity, prove DNS fault domain, refresh lease, confirm gateway.",
        "You ran a complete client-side triage path using every Windows skill from labs 1–3.",
        _win_state(name_map={}, dns=["10.20.30.10"]),
        hints=["hostname", "ipconfig /all", "ping 10.20.30.50", "ping app.training.local", "nslookup app.training.local", "ipconfig /flushdns", "ipconfig /release", "ipconfig /renew", "ping 10.20.30.1"],
        builds_on=["win-ipconfig", "win-dns-break", "win-dhcp-renew"],
    ),
    _lab(
        "w11-inventory",
        "5. Windows 11 VM — Inventory the Endpoint",
        "windows",
        "Treat this as a Windows 11 Education VM. Prove edition, build, user, and hostname.",
        [
            {"id": "winver", "text": "winver or Get-ComputerInfo"},
            {"id": "systeminfo", "text": "systeminfo"},
            {"id": "whoami", "text": "whoami"},
            {"id": "run_hostname", "text": "hostname"},
        ],
        "You are on CIWT-W11-07, a Windows 11 Education training VM. Inventory it before you change anything.",
        "You can identify edition, build, signed-in user, and computer name — the start of every Win11 ticket.",
        _win_state(),
        hints=["winver", "systeminfo", "whoami", "hostname"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "w11-powershell-net",
        "6. Windows 11 VM — PowerShell Network View",
        "windows",
        "Same VM, modern cmdlets: Get-NetIPConfiguration, Get-NetAdapter, Test-Connection.",
        [
            {"id": "ps_shell", "text": "Switch to PowerShell"},
            {"id": "netip", "text": "Get-NetIPConfiguration"},
            {"id": "netadapter", "text": "Get-NetAdapter"},
            {"id": "test_conn", "text": "Test-Connection 10.20.30.1"},
        ],
        "Help desk asked for the Settings > Network & internet view, from CLI. Use PowerShell on the Win11 VM.",
        "You can read adapter, IPv4, gateway, and DNS from PowerShell the way a Win11 tech does.",
        _win_state(),
        hints=["powershell", "Get-NetIPConfiguration", "Get-NetAdapter", "Test-Connection 10.20.30.1"],
        builds_on=["win-ipconfig", "w11-inventory"],
    ),
    _lab(
        "w11-services",
        "7. Windows 11 VM — Service Health",
        "windows",
        "Confirm DHCP, DNS Client, and Defender are running on the Win11 VM.",
        [
            {"id": "svc_dhcp", "text": "Get-Service Dhcp"},
            {"id": "svc_dns", "text": "Get-Service Dnscache"},
            {"id": "svc_def", "text": "Get-Service WinDefend"},
        ],
        "Ticket says 'network settings look fine but nothing renews.' Check the services that own the stack.",
        "You can name the Windows 11 services behind DHCP, DNS cache, and Defender.",
        _win_state(),
        hints=["Get-Service Dhcp", "Get-Service Dnscache", "Get-Service WinDefend"],
        builds_on=["w11-inventory", "w11-powershell-net"],
    ),
    _lab(
        "w11-netsh",
        "7b. Windows 11 VM — netsh interface view",
        "windows",
        "netsh is the older admin path. Same facts as ipconfig, different tool.",
        [
            {"id": "run_ipconfig", "text": "ipconfig /all"},
            {"id": "netsh", "text": "netsh interface ip show config"},
        ],
        "Some tickets still say 'use netsh.' Prove you can read the Ethernet IPv4 block both ways.",
        "You can pull address, mask, gateway, and DNS from netsh as well as ipconfig.",
        _win_state(),
        hints=["ipconfig /all", "netsh interface ip show config"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "w11-processes",
        "7c. Windows 11 VM — What's running",
        "windows",
        "tasklist / Get-Process — prove the shell can list processes before you kill anything.",
        [
            {"id": "tasklist", "text": "tasklist"},
            {"id": "get_process", "text": "Get-Process"},
        ],
        "Slow logon tickets start with 'what is running,' not with Task Manager guesses.",
        "You can list processes from cmd and from PowerShell.",
        _win_state(),
        hints=["tasklist", "powershell", "Get-Process"],
        builds_on=["w11-inventory"],
    ),
    _lab(
        "gui-about",
        "8. Windows 11 GUI — Settings About",
        "win11gui",
        "Win+I path: Settings → System → About. Same clicks on a real Windows 11 PC.",
        [
            {"id": "open_settings", "text": "Open Settings (Start or the Settings icon)"},
            {"id": "open_system", "text": "Open System in the left nav"},
            {"id": "open_about", "text": "Open About and read device name, edition, version, build"},
        ],
        "On a real PC this is Win+I → System → About. Practice that path here.",
        "You used the same About path a tech uses on a live Windows 11 PC.",
        _win_state(),
        hints=["Start → Settings or the Settings icon", "System", "About"],
    ),
    _lab(
        "gui-ethernet",
        "9. Windows 11 GUI — Ethernet properties",
        "win11gui",
        "Win+I path: Settings → Network & internet → Ethernet. Same facts as ipconfig /all.",
        [
            {"id": "open_settings", "text": "Open Settings"},
            {"id": "open_network", "text": "Open Network & internet"},
            {"id": "open_ethernet", "text": "Open Ethernet and read IPv4, gateway, DNS"},
        ],
        "Help desk wants the same facts as ipconfig /all, from the GUI.",
        "You can find IPv4, gateway, and DNS in Settings > Network & internet > Ethernet.",
        _win_state(),
        hints=["Settings", "Network & internet", "Ethernet"],
    ),
    _lab(
        "gui-renew",
        "10. Windows 11 GUI — Renew the Ethernet lease",
        "win11gui",
        "Real lease recycle: Settings → Advanced network settings → More adapter options (ncpa.cpl) → Disable → Enable.",
        [
            {"id": "open_settings", "text": "Open Settings"},
            {"id": "open_network", "text": "Open Network & internet"},
            {"id": "open_ethernet", "text": "Open Advanced network settings / Network Connections"},
            {"id": "toggle_lease", "text": "Disable the Ethernet adapter, then Enable it"},
        ],
        "Do not hunt for Renew on the Ethernet page — Windows 11 does not put it there. Use ncpa.cpl Disable/Enable.",
        "You recycled the GUI connection the way a Win11 user would.",
        _win_state(),
        hints=["Settings → Network & internet → Ethernet", "Disconnect", "Connect"],
        builds_on=["gui-ethernet"],
    ),
    _lab(
        "gui-services",
        "11. Windows 11 GUI — Services",
        "win11gui",
        "Open Services from the desktop and confirm DHCP Client, DNS Client, and Microsoft Defender Antivirus.",
        [
            {"id": "open_services", "text": "Open Services (Start search or services.msc)"},
            {"id": "find_dhcp", "text": "Select DHCP Client (Running)"},
            {"id": "find_dns", "text": "Select DNS Client (Running)"},
            {"id": "find_defend", "text": "Select Microsoft Defender Antivirus Service"},
        ],
        "When the GUI network page looks fine but leases never refresh, check the service that owns DHCP.",
        "You can locate the three services that sit behind address, name, and Defender.",
        _win_state(),
        hints=["Double-click Services", "Scroll or click DHCP Client, DNS Client, Defender"],
    ),
    _lab(
        "gui-update",
        "12. Windows 11 GUI — Windows Update",
        "win11gui",
        "Win+I → Windows Update. Check that the training image is up to date.",
        [
            {"id": "open_settings", "text": "Open Settings"},
            {"id": "open_update", "text": "Open Windows Update"},
        ],
        "On a real PC this is the first place you look before blaming an app for a broken patch Tuesday.",
        "You opened the same Windows Update page a user sees.",
        _win_state(),
        hints=["Settings", "Windows Update"],
    ),
    _lab(
        "gui-accounts",
        "13. Windows 11 GUI — Accounts",
        "win11gui",
        "Settings → Accounts. Read who is signed in before you change a password.",
        [
            {"id": "open_settings", "text": "Open Settings"},
            {"id": "open_accounts", "text": "Open Accounts and read the signed-in user"},
        ],
        "Wrong-user tickets start here. Do not reset a password until you can name the account.",
        "You found the signed-in account on the Accounts page.",
        _win_state(),
        hints=["Settings", "Accounts"],
    ),
    # ── Switch foundation ───────────────────────────────────────────
    _lab(
        "sw-vlan-access",
        "5. Switch — VLAN + Access Port",
        "switch",
        "Create VLAN 20 and place Fa0/2 in it.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "vlan20", "text": "Create VLAN 20 (name optional)"},
            {"id": "access", "text": "Fa0/2 access VLAN 20"},
            {"id": "verify", "text": "show vlan brief"},
        ],
        "User on Fa0/2 must land in VLAN 20 TRAINING-USERS.",
        "VLAN 20 exists and Fa0/2 is an access port in VLAN 20.",
        _sw_state(),
        hints=["enable", "configure terminal", "vlan 20", "name TRAINING-USERS", "interface fa0/2", "switchport mode access", "switchport access vlan 20", "end", "show vlan brief"],
    ),
    _lab(
        "sw-trunk-basics",
        "6. Switch — Trunk Uplink",
        "switch",
        "Reuse enable/conf t; turn Fa0/1 into a trunk (VLAN 20 already exists).",
        [
            {"id": "enable", "text": "enable"},
            {"id": "trunk", "text": "Fa0/1 switchport mode trunk"},
            {"id": "verify_trunk", "text": "show running-config"},
        ],
        "Uplink must carry multiple VLANs. Access ports stay access; uplinks are trunks.",
        "You configured a trunk uplink and can explain access vs trunk.",
        _sw_state(
            vlans={1: "default", 20: "TRAINING-USERS"},
            interfaces={
                "FastEthernet0/1": {"mode": "access", "vlan": 1, "up": True, "trunk": False},
                "FastEthernet0/2": {"mode": "access", "vlan": 20, "up": True, "trunk": False},
            },
        ),
        hints=["enable", "configure terminal", "interface fa0/1", "switchport mode trunk", "end", "show running-config"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "sw-vlan-and-trunk",
        "7. Switch — VLAN + Access + Trunk (capstone)",
        "switch",
        "Combine labs 5–6: create VLAN, access port, and trunk uplink.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "vlan20", "text": "vlan 20"},
            {"id": "access", "text": "Fa0/2 access VLAN 20"},
            {"id": "trunk", "text": "Fa0/1 trunk"},
            {"id": "verify", "text": "show vlan brief"},
            {"id": "verify_trunk", "text": "show running-config"},
        ],
        "Build a complete access edge: VLAN 20, user port Fa0/2, uplink trunk Fa0/1.",
        "You built a complete access-layer edge using every switch skill from labs 5–6.",
        _sw_state(),
        hints=["enable", "conf t", "vlan 20", "name TRAINING-USERS", "interface fa0/2", "switchport mode access", "switchport access vlan 20", "interface fa0/1", "switchport mode trunk", "end", "show vlan brief", "show running-config"],
        builds_on=["sw-vlan-access", "sw-trunk-basics"],
    ),
    # ── Router foundation ───────────────────────────────────────────
    _lab(
        "rtr-gateway",
        "8. Router — Gateway Address + Ping",
        "router",
        "Address Gi0/0 and ping the lab PC.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 = 10.20.0.1/24 + no shutdown"},
            {"id": "show_ip", "text": "show ip interface brief"},
            {"id": "ping_pc", "text": "ping 10.20.0.10"},
        ],
        "R1 is the gateway for 10.20.0.0/24. PC is 10.20.0.10.",
        "Interface is up and you can ping the lab PC.",
        _rtr_state(hosts={"10.20.0.10": True}),
        hints=["enable", "configure terminal", "interface Gi0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "end", "show ip interface brief", "ping 10.20.0.10"],
    ),
    _lab(
        "rtr-two-interfaces",
        "9. Router — Two Connected Networks",
        "router",
        "Reuse gateway skills; bring up a second LAN.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 = 10.20.0.1/24 up"},
            {"id": "addr2", "text": "Gi0/1 = 10.30.0.1/24 up"},
            {"id": "show_ip", "text": "show ip interface brief"},
            {"id": "ping_pc", "text": "ping 10.20.0.10"},
            {"id": "ping_pc2", "text": "ping 10.30.0.20"},
        ],
        "User LAN 10.20.0.0/24 and printer LAN 10.30.0.0/24 — both must be up.",
        "Both interfaces are up and both hosts answer ping.",
        _rtr_state(),
        hints=["enable", "conf t", "interface Gi0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "interface Gi0/1", "ip address 10.30.0.1 255.255.255.0", "no shutdown", "end", "show ip interface brief", "ping 10.20.0.10", "ping 10.30.0.20"],
        builds_on=["rtr-gateway"],
    ),
    _lab(
        "rtr-edge-complete",
        "10. Router — Edge Complete (capstone)",
        "router",
        "Two LANs, verify routes, ping both hosts — full edge router path.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 addressed and up"},
            {"id": "addr2", "text": "Gi0/1 addressed and up"},
            {"id": "show_ip", "text": "show ip interface brief"},
            {"id": "show_route", "text": "show ip route"},
            {"id": "ping_pc", "text": "ping 10.20.0.10"},
            {"id": "ping_pc2", "text": "ping 10.30.0.20"},
        ],
        "Finish the edge: dual interfaces, connected routes visible, both hosts reachable.",
        "You completed a full edge-router bring-up using every router skill from labs 8–9.",
        _rtr_state(),
        hints=["enable", "conf t", "interface Gi0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "interface Gi0/1", "ip address 10.30.0.1 255.255.255.0", "no shutdown", "end", "show ip interface brief", "show ip route", "ping 10.20.0.10", "ping 10.30.0.20"],
        builds_on=["rtr-gateway", "rtr-two-interfaces"],
    ),
    _lab(
        "sw-hostname-write",
        "11. Switch — Hostname and save",
        "switch",
        "Name the switch and write memory. Config that is not saved dies on reload.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "hostname", "text": "hostname SW-ACCESS-01"},
            {"id": "write", "text": "write memory or copy run start"},
        ],
        "Closet switch with no name is a ticket magnet. Set hostname, then save.",
        "The switch has a name and the running-config is saved.",
        _sw_state(),
        hints=["enable", "conf t", "hostname SW-ACCESS-01", "end", "write memory"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "rtr-hostname-write",
        "12. Router — Hostname and save",
        "router",
        "Same save discipline on the router.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "hostname", "text": "hostname R1"},
            {"id": "write", "text": "write memory or copy run start"},
        ],
        "Name the router and copy running-config to startup-config.",
        "Hostname is set and the config is saved.",
        _rtr_state(),
        hints=["enable", "conf t", "hostname R1", "end", "copy running-config startup-config"],
        builds_on=["rtr-gateway"],
    ),
    _lab(
        "w11-firewall",
        "Windows 11 VM — Firewall profiles",
        "windows",
        "Read Domain/Private/Public profile state with netsh advfirewall.",
        [
            {"id": "fw", "text": "netsh advfirewall show allprofiles"},
        ],
        "Before you turn a firewall off, prove which profile is on. That is a CIWT support habit.",
        "You can read Windows Defender Firewall profile state from CLI.",
        _win_state(),
        hints=["netsh advfirewall show allprofiles"],
        builds_on=["w11-inventory"],
    ),
    _lab(
        "w11-disk",
        "Windows 11 VM — List disks",
        "windows",
        "list disk — see number, size, and GPT/MBR before you wipe anything.",
        [
            {"id": "listdisk", "text": "list disk"},
        ],
        "Storage tickets start with inventory. Never clean a disk you have not listed.",
        "You listed the virtual disks on the training VM.",
        _win_state(),
        hints=["list disk"],
        builds_on=["w11-inventory"],
    ),
    _lab(
        "gui-devices",
        "Windows 11 GUI — Device Manager",
        "win11gui",
        "Open Device Manager and find Network adapters and Display adapters.",
        [
            {"id": "open_devmgr", "text": "Open Device Manager"},
            {"id": "find_nic", "text": "Expand Network adapters"},
            {"id": "find_display", "text": "Expand Display adapters"},
        ],
        "Yellow bangs live here. Same tree as devmgmt.msc on a real PC.",
        "You opened the Device Manager tree a tech uses for driver tickets.",
        _win_state(),
        hints=["Start → Device Manager", "Network adapters", "Display adapters"],
    ),
    _lab(
        "sw-port-security",
        "Switch — Port security on an access port",
        "switch",
        "Limit Fa0/2 to one MAC so a user hub cannot cascade.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "access", "text": "Fa0/2 access VLAN 20"},
            {"id": "portsec", "text": "switchport port-security on Fa0/2"},
        ],
        "Port security is an access-layer control. Practice it after the VLAN lab.",
        "Fa0/2 is an access port with port-security enabled.",
        _sw_state(),
        hints=["enable", "conf t", "vlan 20", "int fa0/2", "switchport mode access", "switchport access vlan 20", "switchport port-security", "end"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "rtr-default-route",
        "Router — Default route to the WAN",
        "router",
        "Add ip route 0.0.0.0 0.0.0.0 10.20.0.2 and confirm it in show ip route.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 up with 10.20.0.1"},
            {"id": "defroute", "text": "ip route 0.0.0.0 0.0.0.0 10.20.0.2"},
            {"id": "show_route", "text": "show ip route"},
        ],
        "A LAN with no default route cannot reach the internet. Practice that default route here.",
        "The router has a connected LAN and a default route.",
        _rtr_state(),
        hints=["enable", "conf t", "int g0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "ip route 0.0.0.0 0.0.0.0 10.20.0.2", "end", "show ip route"],
        builds_on=["rtr-gateway"],
    ),
    _lab(
        "sw-banner",
        "Switch — Login banner",
        "switch",
        "Set a login banner so the closet switch identifies the command.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "banner", "text": "banner login"},
        ],
        "A nameless switch with no banner is how boxes get the wrong cable in a hurry.",
        "The switch has a login banner.",
        _sw_state(),
        hints=["enable", "conf t", "banner login CIWT-ACCESS"],
        builds_on=["sw-hostname-write"],
    ),
    _lab(
        "w11-wlan",
        "Windows 11 VM — WLAN report",
        "windows",
        "netsh wlan show interfaces — even if this VM is Ethernet-only, know the command.",
        [
            {"id": "wlan", "text": "netsh wlan show interfaces"},
        ],
        "Wireless tickets start with which SSID and radio state, not with a reboot.",
        "You ran the WLAN interface report.",
        _win_state(),
        hints=["netsh wlan show interfaces"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "sw-mac-table",
        "Switch — MAC address table",
        "switch",
        "show mac address-table — prove the switch learned a user MAC.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "show_mac", "text": "show mac address-table"},
        ],
        "Layer-2 tickets start here: which port learned the PC.",
        "You read the MAC table.",
        _sw_state(),
        hints=["enable", "show mac address-table"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "rtr-describe",
        "Router — Interface description",
        "router",
        "Label Gi0/0 so the next watch knows what the cable is.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 addressed and up"},
            {"id": "desc", "text": "description USERS-LAN"},
        ],
        "An undescribed interface is how the wrong link gets shut.",
        "Gi0/0 is up and labeled.",
        _rtr_state(),
        hints=["enable", "conf t", "int g0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "description USERS-LAN"],
        builds_on=["rtr-gateway"],
    ),
    _lab(
        "win-arp",
        "Windows 11 VM — ARP cache",
        "windows",
        "arp -a — see the gateway MAC after you have an address.",
        [
            {"id": "run_ipconfig", "text": "ipconfig"},
            {"id": "arp", "text": "arp -a"},
        ],
        "If ping works but ARP is empty, you are not on the same L2 segment you think you are.",
        "You listed the ARP cache.",
        _win_state(),
        hints=["ipconfig", "arp -a"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "sw-int-status",
        "Switch — Interface status",
        "switch",
        "show interfaces status — connected vs disabled, access vs trunk.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "int_status", "text": "show interfaces status"},
        ],
        "Before you blame the PC, look at the port.",
        "You read interface status.",
        _sw_state(),
        hints=["enable", "show interfaces status"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "rtr-trace",
        "Router — Traceroute",
        "router",
        "traceroute 10.20.0.10 from the router after the LAN is up.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "addr", "text": "Gi0/0 up"},
            {"id": "trace", "text": "traceroute 10.20.0.10"},
        ],
        "Ping says yes or no. Traceroute says where it stopped.",
        "You traced to the LAN host.",
        _rtr_state(),
        hints=["enable", "conf t", "int g0/0", "ip address 10.20.0.1 255.255.255.0", "no shutdown", "end", "traceroute 10.20.0.10"],
        builds_on=["rtr-gateway"],
    ),
    _lab(
        "win-route",
        "Windows 11 VM — Route table",
        "windows",
        "route print — default gateway and on-link subnet.",
        [
            {"id": "route", "text": "route print"},
        ],
        "If ping dies after a VPN or static route, this table is the evidence.",
        "You printed the IPv4 route table.",
        _win_state(),
        hints=["route print"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "win-getmac",
        "Windows 11 VM — MAC address",
        "windows",
        "getmac — the L2 identity you will see on the switch CAM table.",
        [
            {"id": "getmac", "text": "getmac"},
        ],
        "Switch MAC table plus getmac is how you prove the drop is this PC.",
        "You printed the adapter MAC.",
        _win_state(),
        hints=["getmac"],
        builds_on=["win-arp"],
    ),
    _lab(
        "win-netstat",
        "Windows 11 VM — Active connections",
        "windows",
        "netstat -an — what is talking on this box right now.",
        [
            {"id": "netstat", "text": "netstat -an"},
        ],
        "Before you reboot a 'slow PC', see if it is waiting on DNS.",
        "You listed active connections.",
        _win_state(),
        hints=["netstat -an"],
        builds_on=["w11-processes"],
    ),
    _lab(
        "win-hostname",
        "Windows 11 VM — Hostname",
        "windows",
        "hostname — the name you will see in tickets and DHCP.",
        [{"id": "run_hostname", "text": "hostname"}],
        "Never start a ticket without the computer name.",
        "You printed the host name.",
        _win_state(),
        hints=["hostname"],
        builds_on=["w11-inventory"],
    ),
    _lab(
        "win-ping-loop",
        "Windows 11 VM — Loopback ping",
        "windows",
        "ping 127.0.0.1 — stack alive before you blame the cable.",
        [{"id": "ping_loop", "text": "ping 127.0.0.1"}],
        "If loopback fails, the NIC is not the first problem.",
        "Loopback replied.",
        _win_state(),
        hints=["ping 127.0.0.1"],
        builds_on=["win-ipconfig"],
    ),
    _lab(
        "win-nslookup-ok",
        "Windows 11 VM — Working name lookup",
        "windows",
        "nslookup a name that exists in this lab map.",
        [{"id": "ns_ok", "text": "nslookup files.training.local"}],
        "You already practiced a failed lookup. This one should resolve.",
        "The name resolved.",
        _win_state(name_map={"files.training.local": "10.20.30.50"}),
        hints=["nslookup files.training.local"],
        builds_on=["win-dns-break"],
    ),
    _lab(
        "win-flushdns",
        "Windows 11 VM — Flush DNS cache",
        "windows",
        "ipconfig /flushdns after a bad name.",
        [{"id": "flush_dns", "text": "ipconfig /flushdns"}],
        "Stale cache looks like a DNS outage.",
        "Resolver cache flushed.",
        _win_state(),
        hints=["ipconfig /flushdns"],
        builds_on=["win-dns-break"],
    ),
    _lab(
        "sw-show-ver",
        "Switch — show version",
        "switch",
        "show version — image and uptime before you reload.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "show_ver", "text": "show version"},
        ],
        "Never reload a box you have not identified.",
        "You read the switch version.",
        _sw_state(),
        hints=["enable", "show version"],
        builds_on=["sw-hostname-write"],
    ),
    _lab(
        "sw-describe",
        "Switch — Access port description",
        "switch",
        "Describe Fa0/2 so the drop is labeled.",
        [
            {"id": "enable", "text": "enable"},
            {"id": "desc", "text": "description USER-DROP"},
        ],
        "Unlabeled user drops waste the next watch.",
        "Fa0/2 is labeled.",
        _sw_state(),
        hints=["enable", "conf t", "int fa0/2", "description USER-DROP"],
        builds_on=["sw-vlan-access"],
    ),
    _lab(
        "ticket-intake",
        "Block 1 — Ticket intake desk",
        "ticket",
        "Classify, set impact, decide escalate, write a usable note, submit.",
        [
            {"id": "showed", "text": "Read the ticket with show ticket"},
            {"id": "classified", "text": "classify break-fix | request | incident"},
            {"id": "impact", "text": "impact 1 | impact many"},
            {"id": "escalated", "text": "escalate yes | escalate no"},
            {"id": "noted", "text": "note <symptom, observation, next step>"},
            {"id": "submitted", "text": "submit the complete intake"},
        ],
        "A user typed one messy sentence. Turn it into an intake another watch can use. Commands are in Chapter 1.5.",
        "Intake is complete: type, impact, escalate decision, and a usable note.",
        {
            "hostname": "TICKET-DESK",
            "ticket": "Half the quarterdeck badges stopped after lunch. The reader by the hatch feels warm.",
            "classify": None,
            "impact": None,
            "escalate": None,
            "note": "",
        },
        hints=["help", "show ticket", "classify incident", "impact many", "escalate yes", "note ...", "submit"],
    ),
    _lab(
        "hw-board",
        "Block 2 — Identify the board on the bench",
        "ticket",
        "Name form factor, socket, memory, storage, and POST from the bench card.",
        [
            {"id": "showed", "text": "show board"},
            {"id": "form", "text": "form-factor microatx | atx | mini-itx"},
            {"id": "socket", "text": "socket lga1700 | am5"},
            {"id": "memory", "text": "memory ddr4 | ddr5"},
            {"id": "storage", "text": "storage nvme | sata"},
            {"id": "post", "text": "post memory | display | power | ok"},
            {"id": "submitted", "text": "submit"},
        ],
        "Side panel is off. Read the card. Commands are in Chapter 2.",
        "Board card complete.",
        {
            "hostname": "BENCH",
            "kind": "hw",
            "card": (
                "CASE: small office tower\n"
                "BOARD: 9.6 x 9.6 in, four DIMM slots, one M.2 short slot with a stick installed\n"
                "SOCKET silkscreen: LGA1700\n"
                "DIMM marking: DDR5\n"
                "POST: debug LED reads MEM — long beeps, no video"
            ),
            "answers": {
                "form-factor": "microatx",
                "socket": "lga1700",
                "memory": "ddr5",
                "storage": "nvme",
                "post": "memory",
            },
            "guess": {},
        },
        hints=["help", "show board", "form-factor microatx", "socket lga1700", "memory ddr5", "storage nvme", "post memory", "submit"],
    ),
]

LABS_BY_ID = {l["id"]: l for l in LABS}

# ── Cisco IOS-style unique-prefix matching + Tab complete ────────────
# A token matches a keyword if it is a non-empty prefix of that keyword
# and does not also uniquely collide. Ambiguous prefixes raise like IOS.

# Commands allowed in each IOS mode. Wrong-mode input must NOT change the prompt.
_COMMON_SHOW_SW = [
    ("show", "vlan", "brief"), ("show", "vlan"),
    ("show", "running-config"), ("show", "startup-config"),
    ("show", "interfaces", "status"), ("show", "interface", "status"),
    ("show", "interfaces"), ("show", "ip", "interface", "brief"),
    ("show", "mac", "address-table"), ("show", "mac", "address", "table"),
    ("show", "version"), ("show", "clock"),
]
_SW_BY_MODE = {
    "user": [
        ("enable",), ("exit",), ("help",), ("?",), ("clear",),
        ("show", "vlan", "brief"), ("show", "vlan"),
        ("show", "interfaces", "status"), ("show", "interface", "status"),
        ("show", "version"),
    ],
    "priv": [
        ("enable",), ("disable",), ("exit",), ("end",),
        ("configure", "terminal"),
        *_COMMON_SHOW_SW,
        ("ping", "*"), ("traceroute", "*"),
        ("copy", "running-config", "startup-config"),
        ("write", "memory"), ("write",),
        ("help",), ("?",), ("clear",),
    ],
    "config": [
        ("hostname", "*"), ("vlan", "*"), ("interface", "*"),
        ("banner", "login"),
        ("banner", "login", "*"),
        ("banner", "motd"),
        ("banner", "motd", "*"),
        ("ip", "default-gateway", "*"),
        ("no", "vlan", "*"),
        ("exit",), ("end",),
        ("do", "show", "vlan", "brief"),
        ("do", "show", "running-config"),
        ("do", "show", "interfaces", "status"),
        ("do", "show", "ip", "interface", "brief"),
        ("help",), ("?",),
    ],
    "config-vlan": [
        ("name", "*"), ("vlan", "*"), ("interface", "*"),
        ("exit",), ("end",),
        ("do", "show", "vlan", "brief"),
        ("help",), ("?",),
    ],
    "config-if": [
        ("switchport", "mode", "access"),
        ("switchport", "mode", "trunk"),
        ("switchport", "access", "vlan", "*"),
        ("switchport", "trunk", "allowed", "vlan", "*"),
        ("switchport", "nonegotiate"),
        ("switchport", "port-security"),
        ("switchport", "port-security", "maximum", "*"),
        ("switchport", "port-security", "mac-address", "sticky"),
        ("switchport", "port-security", "violation", "*"),
        ("description", "*"),
        ("speed", "*"), ("duplex", "*"),
        ("no", "shutdown"), ("shutdown",),
        ("interface", "*"),
        ("exit",), ("end",),
        ("do", "show", "vlan", "brief"),
        ("do", "show", "running-config"),
        ("help",), ("?",),
    ],
}

_RTR_BY_MODE = {
    "user": [
        ("enable",), ("exit",), ("help",), ("?",), ("clear",),
        ("show", "ip", "interface", "brief"), ("show", "version"),
    ],
    "priv": [
        ("enable",), ("disable",), ("exit",), ("end",),
        ("configure", "terminal"),
        ("show", "ip", "interface", "brief"),
        ("show", "ip", "route"),
        ("show", "ip", "protocols"),
        ("show", "running-config"), ("show", "startup-config"),
        ("show", "interfaces"), ("show", "version"),
        ("show", "arp"), ("show", "clock"),
        ("ping", "*"), ("traceroute", "*"),
        ("copy", "running-config", "startup-config"),
        ("write", "memory"), ("write",),
        ("help",), ("?",), ("clear",),
    ],
    "config": [
        ("hostname", "*"), ("interface", "*"),
        ("ip", "route", "*", "*", "*"),
        ("ip", "route", "*", "*"),
        ("exit",), ("end",),
        ("do", "show", "ip", "interface", "brief"),
        ("do", "show", "ip", "route"),
        ("help",), ("?",),
    ],
    "config-if": [
        ("ip", "address", "*", "*"),
        ("no", "shutdown"), ("shutdown",),
        ("description", "*"),
        ("bandwidth", "*"),
        ("interface", "*"),
        ("exit",), ("end",),
        ("do", "show", "ip", "interface", "brief"),
        ("help",), ("?",),
    ],
}

_SWITCH_TEMPLATES = [t for group in _SW_BY_MODE.values() for t in group]
_ROUTER_TEMPLATES = [t for group in _RTR_BY_MODE.values() for t in group]

_WIN_COMMANDS = [
    "hostname",
    "ipconfig",
    "ipconfig /all",
    "ipconfig /release",
    "ipconfig /renew",
    "ipconfig /flushdns",
    "ipconfig /displaydns",
    "ping",
    "tracert",
    "arp -a",
    "route print",
    "netstat -an",
    "getmac",
    "nslookup",
    "whoami",
    "winver",
    "systeminfo",
    "powershell",
    "cmd",
    "Get-ComputerInfo",
    "Get-NetIPConfiguration",
    "Get-NetAdapter",
    "Get-DnsClientServerAddress",
    "Resolve-DnsName",
    "Test-Connection",
    "Get-Service",
    "Get-LocalUser",
    "netsh interface ip show config",
    "tasklist",
    "Get-Process",
    "sfc /scannow",
    "gpupdate /force",
    "help",
    "cls",
    "clear",
]


def _token_matches(abbrev, word):
    if word == "*":
        return True
    if not abbrev:
        return False
    return word.lower().startswith(abbrev.lower())


def _matching_templates(tokens, templates, partial_last=False):
    hits = []
    for tmpl in templates:
        ok = True
        used = 0
        for i, tok in enumerate(tokens):
            if i >= len(tmpl):
                ok = False
                break
            word = tmpl[i]
            if partial_last and i == len(tokens) - 1:
                if word != "*" and not word.lower().startswith(tok.lower()):
                    ok = False
                    break
            else:
                if not _token_matches(tok, word):
                    ok = False
                    break
            used = i + 1
        if ok:
            hits.append(tmpl)
    return hits


_IOS_HELP = {
    "enable": "Turn on privileged commands",
    "disable": "Turn off privileged commands",
    "exit": "Exit from current mode",
    "end": "Exit to privileged EXEC",
    "configure": "Enter configuration mode",
    "terminal": "Configure from the terminal",
    "show": "Show running system information",
    "vlan": "VLAN information / create VLAN",
    "brief": "Brief summary",
    "running-config": "Current operating configuration",
    "startup-config": "Contents of startup configuration",
    "interfaces": "Interface status and configuration",
    "interface": "Select an interface to configure",
    "status": "Status of interfaces",
    "ip": "IP information / IP config",
    "route": "IP routing table / static route",
    "arp": "ARP table",
    "version": "System hardware and software status",
    "clock": "Display the system clock",
    "mac": "MAC address table",
    "address-table": "MAC forwarding table",
    "protocols": "IP routing protocol status",
    "ping": "Send ICMP echo messages",
    "traceroute": "Trace route to destination",
    "copy": "Copy configuration or files",
    "write": "Write running config to memory",
    "memory": "Write to NVRAM",
    "hostname": "Set system's network name",
    "name": "Set VLAN name",
    "switchport": "Layer-2 interface commands",
    "mode": "Access or trunk",
    "access": "Set access mode / access VLAN",
    "trunk": "Set trunk mode / allowed VLANs",
    "allowed": "Allowed VLAN list",
    "nonegotiate": "Disable DTP",
    "description": "Interface description",
    "speed": "Interface speed",
    "duplex": "Interface duplex",
    "shutdown": "Disable the interface",
    "no": "Negate a command",
    "do": "EXEC command from config mode",
    "address": "Set IP address and mask",
    "bandwidth": "Informational bandwidth",
    "default-gateway": "Default gateway on L2 switch",
    "help": "Description of the interactive help system",
    "?": "Context-sensitive help",
    "clear": "Clear the terminal screen",
}


def ios_help(kind, mode, raw):
    """IOS-style '?' help for the current mode. Does not change the prompt."""
    mode = mode or "user"
    templates = (_SW_BY_MODE if kind == "switch" else _RTR_BY_MODE).get(mode) or []
    text = (raw or "").strip()
    if not text or text in ("?", "help"):
        tokens, prefix = [], ""
    elif text.endswith("?"):
        body = text[:-1]
        attached = bool(body) and not body.endswith(" ")
        parts = body.split()
        if attached and parts:
            prefix = parts[-1].lower()
            tokens = parts[:-1]
        else:
            prefix = ""
            tokens = parts
    else:
        tokens, prefix = text.split(), ""

    nxt = {}
    for tmpl in templates:
        if len(tokens) > len(tmpl):
            continue
        ok = True
        for i, tok in enumerate(tokens):
            if i >= len(tmpl) or not _token_matches(tok, tmpl[i]):
                ok = False
                break
        if not ok:
            continue
        if len(tokens) == len(tmpl):
            nxt["<cr>"] = "Carriage return — execute command"
            continue
        word = tmpl[len(tokens)]
        label = "<id>" if word == "*" else word
        if prefix and word != "*" and not word.lower().startswith(prefix):
            continue
        if prefix and word == "*" and not label.startswith(prefix):
            continue
        nxt[label] = _IOS_HELP.get(word, "Command keyword")

    lines = []
    if not nxt:
        lines.append("% Unrecognized command.")
        lines.append("Type ? for a list of available commands in this mode.")
        return lines
    width = max(len(k) for k in nxt)
    for key in sorted(nxt, key=lambda s: (s == "<cr>", s)):
        lines.append(f"  {key:<{width}}  {nxt[key]}")
    lines.append("")
    lines.append("Shortcuts: unique prefixes (en, conf t, sh ip int br, int fa0/2). Tab completes.")
    return lines


def expand_ios_line(line, kind, mode=None):
    """Expand uniquely abbreviated IOS (or accept Windows as-is).
    Returns (expanded_line | None, error_lines).
    Mode-aware: only commands legal in the current hierarchy are matched.
    """
    raw = (line or "").strip()
    if not raw:
        return raw, []
    if kind == "windows":
        return raw, []
    mode = mode or "user"
    if kind == "switch":
        templates = _SW_BY_MODE.get(mode) or _SW_BY_MODE["user"]
    else:
        templates = _RTR_BY_MODE.get(mode) or _RTR_BY_MODE["user"]
    tokens = raw.split()
    hits = _matching_templates(tokens, templates, partial_last=False)
    if not hits:
        # try allowing last token as unique prefix even if shorter than keyword
        hits = _matching_templates(tokens, templates, partial_last=True)
    if not hits:
        return None, ["% Invalid input detected at '^' marker.", "% Incomplete command."]
    # A command is incomplete unless every template slot is filled
    complete_hits = [t for t in hits if len(tokens) >= len(t)]
    if not complete_hits:
        return None, ["% Incomplete command."]
    hits = complete_hits
    # Expand keywords; keep wildcard tokens as typed
    expanded_opts = []
    for tmpl in hits:
        parts = []
        for i, tok in enumerate(tokens):
            word = tmpl[i] if i < len(tmpl) else tok
            parts.append(tok if word == "*" else word)
        expanded_opts.append(" ".join(parts))
    uniq = sorted(set(expanded_opts))
    if len(uniq) == 1:
        return uniq[0], []
    # "en" is enable in user EXEC (end is a different command spelled out)
    prefer = {"en": "enable", "ena": "enable", "enab": "enable", "enabl": "enable"}
    first = tokens[0].lower()
    if first in prefer:
        wanted = prefer[first]
        for cand in uniq:
            if cand.split()[0].lower() == wanted:
                return cand, []
    return None, ["% Ambiguous command:  \"" + raw + "\""]


def complete_ios_line(line, kind, mode=None):
    """Tab-complete current token. Returns {text, options, beep}."""
    raw = line or ""
    ends_space = raw.endswith(" ")
    tokens = raw.split()
    if kind == "windows":
        prefix = raw.lstrip()
        opts = [c for c in _WIN_COMMANDS if c.startswith(prefix.lower()) or c.startswith(prefix)]
        if prefix and not opts:
            opts = [c for c in _WIN_COMMANDS if c.lower().startswith(prefix.lower())]
        if len(opts) == 1:
            return {"text": opts[0] + (" " if not opts[0].endswith("*") else ""), "options": opts, "beep": False}
        return {"text": raw, "options": opts, "beep": len(opts) != 1}

    mode = mode or "user"
    if kind == "switch":
        templates = _SW_BY_MODE.get(mode) or _SW_BY_MODE["user"]
    else:
        templates = _RTR_BY_MODE.get(mode) or _RTR_BY_MODE["user"]
    if not tokens:
        nexts = sorted({t[0] for t in templates if t[0] != "*"})
        return {"text": raw, "options": nexts, "beep": True}

    if ends_space:
        hits = _matching_templates(tokens, templates, partial_last=False)
        nxt = []
        for tmpl in hits:
            if len(tmpl) > len(tokens):
                w = tmpl[len(tokens)]
                if w != "*":
                    nxt.append(w)
        nxt = sorted(set(nxt))
        if len(nxt) == 1:
            return {"text": raw + nxt[0] + " ", "options": nxt, "beep": False}
        return {"text": raw, "options": nxt, "beep": True}

    head, last = tokens[:-1], tokens[-1]
    hits = _matching_templates(tokens, templates, partial_last=True)
    nxt = []
    for tmpl in hits:
        idx = len(head)
        if idx < len(tmpl) and tmpl[idx] != "*":
            if tmpl[idx].lower().startswith(last.lower()):
                nxt.append(tmpl[idx])
    nxt = sorted(set(nxt))
    if len(nxt) == 1:
        rebuilt = (" ".join(head + [nxt[0]]) if head else nxt[0]) + " "
        return {"text": rebuilt, "options": nxt, "beep": False}
    return {"text": raw, "options": nxt, "beep": True}

# Expected sequences for self-test (every lab must pass)
VERIFY_SEQUENCES = {
    "ticket-intake": (
        [
            "show ticket",
            "classify incident",
            "impact many",
            "escalate yes",
            "note Badge readers failed after lunch. Reader surface warm. Did not open panel. Need facilities on scene.",
            "submit",
        ],
        ["showed", "classified", "impact", "escalated", "noted", "submitted"],
    ),
    "hw-board": (
        [
            "show board",
            "form-factor microatx",
            "socket lga1700",
            "memory ddr5",
            "storage nvme",
            "post memory",
            "submit",
        ],
        ["showed", "form", "socket", "memory", "storage", "post", "submitted"],
    ),
    "win-ipconfig": (["hostname", "ipconfig /all"], ["run_hostname", "run_ipconfig"]),
    "win-dns-break": (
        ["ipconfig /all", "ping 10.20.30.50", "ping app.training.local", "nslookup app.training.local", "ipconfig /flushdns"],
        ["run_ipconfig", "ping_ip_ok", "ping_name_fail", "nslookup_fail", "flush_dns"],
    ),
    "win-dhcp-renew": (
        ["ipconfig /all", "ipconfig /release", "ipconfig /renew", "ping 10.20.30.1"],
        ["run_ipconfig", "release", "renew", "ping_gw"],
    ),
    "win-full-triage": (
        [
            "hostname", "ipconfig /all", "ping 10.20.30.50", "ping app.training.local",
            "nslookup app.training.local", "ipconfig /flushdns", "ipconfig /release",
            "ipconfig /renew", "ping 10.20.30.1",
        ],
        ["run_hostname", "run_ipconfig", "ping_ip_ok", "ping_name_fail", "nslookup_fail", "flush_dns", "release", "renew", "ping_gw"],
    ),
    "w11-inventory": (
        ["winver", "systeminfo", "whoami", "hostname"],
        ["winver", "systeminfo", "whoami", "run_hostname"],
    ),
    "w11-powershell-net": (
        ["powershell", "Get-NetIPConfiguration", "Get-NetAdapter", "Test-Connection 10.20.30.1"],
        ["ps_shell", "netip", "netadapter", "test_conn"],
    ),
    "w11-services": (
        ["Get-Service Dhcp", "Get-Service Dnscache", "Get-Service WinDefend"],
        ["svc_dhcp", "svc_dns", "svc_def"],
    ),
    "w11-netsh": (
        ["ipconfig /all", "netsh interface ip show config"],
        ["run_ipconfig", "netsh"],
    ),
    "w11-processes": (
        ["tasklist", "Get-Process"],
        ["tasklist", "get_process"],
    ),
    "sw-hostname-write": (
        ["enable", "configure terminal", "hostname SW-ACCESS-01", "end", "write memory"],
        ["enable", "hostname", "write"],
    ),
    "rtr-hostname-write": (
        ["enable", "configure terminal", "hostname R1", "end", "write memory"],
        ["enable", "hostname", "write"],
    ),
    "w11-firewall": (
        ["netsh advfirewall show allprofiles"],
        ["fw"],
    ),
    "w11-disk": (
        ["list disk"],
        ["listdisk"],
    ),
    "sw-port-security": (
        [
            "enable", "conf t", "vlan 20", "interface fa0/2",
            "switchport mode access", "switchport access vlan 20",
            "switchport port-security", "end",
        ],
        ["enable", "access", "portsec"],
    ),
    "sw-banner": (
        ["enable", "configure terminal", "banner login"],
        ["enable", "banner"],
    ),
    "w11-wlan": (
        ["netsh wlan show interfaces"],
        ["wlan"],
    ),
    "sw-mac-table": (
        ["enable", "show mac address-table"],
        ["enable", "show_mac"],
    ),
    "rtr-describe": (
        [
            "enable", "conf t", "interface Gi0/0",
            "ip address 10.20.0.1 255.255.255.0", "no shutdown",
            "description USERS-LAN",
        ],
        ["enable", "addr", "desc"],
    ),
    "win-arp": (
        ["ipconfig", "arp -a"],
        ["run_ipconfig", "arp"],
    ),
    "sw-int-status": (
        ["enable", "show interfaces status"],
        ["enable", "int_status"],
    ),
    "rtr-trace": (
        [
            "enable", "conf t", "interface Gi0/0",
            "ip address 10.20.0.1 255.255.255.0", "no shutdown",
            "end", "traceroute 10.20.0.10",
        ],
        ["enable", "addr", "trace"],
    ),
    "win-route": (["route print"], ["route"]),
    "win-getmac": (["getmac"], ["getmac"]),
    "win-netstat": (["netstat -an"], ["netstat"]),
    "win-hostname": (["hostname"], ["run_hostname"]),
    "win-ping-loop": (["ping 127.0.0.1"], ["ping_loop"]),
    "win-nslookup-ok": (["nslookup files.training.local"], ["ns_ok"]),
    "win-flushdns": (["ipconfig /flushdns"], ["flush_dns"]),
    "sw-show-ver": (["enable", "show version"], ["enable", "show_ver"]),
    "sw-describe": (
        ["enable", "conf t", "interface fa0/2", "description USER-DROP"],
        ["enable", "desc"],
    ),
    "rtr-default-route": (
        [
            "enable", "conf t", "interface Gi0/0",
            "ip address 10.20.0.1 255.255.255.0", "no shutdown",
            "exit", "ip route 0.0.0.0 0.0.0.0 10.20.0.2", "end", "show ip route",
        ],
        ["enable", "addr", "defroute", "show_route"],
    ),
    "sw-vlan-access": (
        [
            "enable", "configure terminal", "vlan 20", "name TRAINING-USERS",
            "interface fa0/2", "switchport mode access", "switchport access vlan 20",
            "end", "show vlan brief",
        ],
        ["enable", "vlan20", "access", "verify"],
    ),
    "sw-trunk-basics": (
        ["enable", "conf t", "interface fa0/1", "switchport mode trunk", "end", "show running-config"],
        ["enable", "trunk", "verify_trunk"],
    ),
    "sw-vlan-and-trunk": (
        [
            "enable", "conf t", "vlan 20", "interface fa0/2", "switchport mode access",
            "switchport access vlan 20", "interface fa0/1", "switchport mode trunk",
            "end", "show vlan brief", "show running-config",
        ],
        ["enable", "vlan20", "access", "trunk", "verify", "verify_trunk"],
    ),
    "rtr-gateway": (
        [
            "enable", "configure terminal", "interface Gi0/0",
            "ip address 10.20.0.1 255.255.255.0", "no shutdown", "end",
            "show ip interface brief", "ping 10.20.0.10",
        ],
        ["enable", "addr", "show_ip", "ping_pc"],
    ),
    "rtr-two-interfaces": (
        [
            "enable", "conf t", "interface Gi0/0", "ip address 10.20.0.1 255.255.255.0",
            "no shutdown", "interface Gi0/1", "ip address 10.30.0.1 255.255.255.0",
            "no shutdown", "end", "show ip interface brief", "ping 10.20.0.10", "ping 10.30.0.20",
        ],
        ["enable", "addr", "addr2", "show_ip", "ping_pc", "ping_pc2"],
    ),
    "rtr-edge-complete": (
        [
            "enable", "conf t", "interface Gi0/0", "ip address 10.20.0.1 255.255.255.0",
            "no shutdown", "interface Gi0/1", "ip address 10.30.0.1 255.255.255.0",
            "no shutdown", "end", "show ip interface brief", "show ip route",
            "ping 10.20.0.10", "ping 10.30.0.20",
        ],
        ["enable", "addr", "addr2", "show_ip", "show_route", "ping_pc", "ping_pc2"],
    ),
}


# Curriculum chapter → live labs (course code, module order)
CHAPTER_LABS = {
    ("ITSUP", 1): ["ticket-intake"],
    ("ITSUP", 2): ["hw-board"],
    ("ITSUP", 3): ["w11-disk", "gui-devices"],
    ("ITSUP", 5): ["win-ipconfig", "win-dns-break", "w11-inventory", "w11-netsh", "gui-ethernet", "win-hostname", "win-ping-loop", "win-nslookup-ok", "win-flushdns", "win-arp", "win-route", "w11-wlan"],
    ("ITSUP", 8): ["w11-inventory", "w11-powershell-net", "w11-services", "win-dhcp-renew", "gui-about", "gui-services", "gui-update", "gui-accounts"],
    ("ITSUP", 10): ["gui-accounts", "gui-services", "w11-firewall"],
    ("ITSUP", 13): ["w11-inventory", "win-ipconfig", "win-dns-break", "win-dhcp-renew", "win-full-triage", "w11-powershell-net", "w11-netsh", "w11-processes", "w11-firewall", "w11-disk", "gui-about", "gui-ethernet", "gui-renew", "gui-update", "gui-accounts", "gui-devices"],
    ("NETOPS", 1): ["win-ipconfig"],
    ("NETOPS", 2): ["sw-vlan-access", "sw-trunk-basics", "sw-vlan-and-trunk", "sw-port-security", "sw-mac-table", "sw-banner", "sw-int-status", "sw-show-ver", "sw-describe"],
    ("NETOPS", 3): ["rtr-gateway", "rtr-two-interfaces", "rtr-edge-complete", "rtr-default-route", "rtr-describe"],
    ("NETOPS", 4): ["win-dns-break", "win-dhcp-renew"],
    ("NETOPS", 6): ["win-full-triage", "sw-vlan-and-trunk", "rtr-edge-complete"],
    ("NETOPS", 9): [
        "sw-vlan-access", "sw-trunk-basics", "sw-vlan-and-trunk",
        "rtr-gateway", "rtr-two-interfaces", "rtr-edge-complete",
        "sw-hostname-write", "rtr-hostname-write",
    ],
}


def labs_for_course(course):
    """Every lab that belongs to this curriculum set, in catalog order."""
    code = (getattr(course, "code", None) or "") if course is not None else ""
    ids = []
    for (c, _order), lab_ids in CHAPTER_LABS.items():
        if c == code:
            for i in lab_ids:
                if i not in ids:
                    ids.append(i)
    for (c, _ch, _lo), lab_ids in LESSON_LABS.items():
        if c == code:
            for i in lab_ids:
                if i not in ids:
                    ids.append(i)
    if not ids:
        if code == "ITSUP":
            ids = [l["id"] for l in LABS if l["kind"] == "windows"]
        elif code == "NETOPS":
            ids = [l["id"] for l in LABS if l["kind"] in ("switch", "router", "windows")]
        else:
            ids = [l["id"] for l in LABS]
    labs = []
    for i in ids:
        lab = LABS_BY_ID.get(i)
        if lab:
            item = {
                "id": lab["id"],
                "title": lab["title"],
                "kind": lab["kind"],
                "blurb": lab["blurb"],
                "align": LAB_ALIGN.get(lab["id"], lab.get("blurb") or ""),
            }
            labs.append(item)
    return labs


def labs_for_module(module):
    """Labs that belong in this chapter."""
    if not module:
        return []
    course = getattr(module, "course", None)
    code = (getattr(course, "code", None) or "")
    order = getattr(module, "order", None)
    ids = list(CHAPTER_LABS.get((code, order), []))
    if not ids:
        title = (getattr(module, "title", "") or "").lower()
        if any(k in title for k in ("foundation", "workplace", "ticket", "safety")):
            ids = ["ticket-intake"]
        elif any(k in title for k in ("motherboard", "architecture", "cpu", "memory")):
            ids = ["hw-board"]
        elif any(k in title for k in ("vlan", "switch", "trunk")):
            ids = ["sw-vlan-access", "sw-trunk-basics", "sw-vlan-and-trunk"]
        elif any(k in title for k in ("rout", "wan", "gateway")):
            ids = ["rtr-gateway", "rtr-two-interfaces", "rtr-edge-complete"]
        elif any(k in title for k in ("windows cli", "dhcp", "dns", "ipconfig")):
            ids = ["win-ipconfig", "win-dns-break", "win-dhcp-renew", "win-full-triage"]
        elif "cli lab" in title:
            ids = [l["id"] for l in LABS]
    return [LABS_BY_ID[i] for i in ids if i in LABS_BY_ID]


# Specific lesson (course, chapter order, lesson order) → labs to embed
LESSON_LABS = {
    ("ITSUP", 1, 1): ["ticket-intake"],
    ("ITSUP", 1, 2): ["ticket-intake"],
    ("ITSUP", 1, 3): ["ticket-intake"],
    ("ITSUP", 1, 4): ["ticket-intake"],
    ("ITSUP", 1, 5): ["ticket-intake"],
    ("ITSUP", 2, 1): ["hw-board"],
    ("ITSUP", 2, 2): ["hw-board"],
    ("ITSUP", 2, 3): ["hw-board"],
    ("ITSUP", 2, 4): ["hw-board"],
    ("ITSUP", 2, 5): ["hw-board"],
    ("ITSUP", 5, 1): ["win-ipconfig"],
    ("ITSUP", 5, 3): ["win-ipconfig", "win-dns-break"],
    ("ITSUP", 5, 5): ["win-full-triage"],
    ("ITSUP", 8, 1): ["w11-inventory", "gui-about"],
    ("ITSUP", 8, 2): ["win-dhcp-renew", "w11-powershell-net", "gui-ethernet"],
    ("ITSUP", 8, 3): ["w11-services", "gui-services"],
    ("ITSUP", 13, 1): ["w11-inventory", "gui-about"],
    ("ITSUP", 13, 2): ["win-ipconfig", "w11-powershell-net", "gui-ethernet"],
    ("ITSUP", 13, 3): ["win-dhcp-renew", "gui-renew"],
    ("ITSUP", 13, 4): ["win-dns-break", "win-full-triage"],
    ("ITSUP", 13, 5): ["gui-about", "gui-ethernet", "gui-renew", "gui-services", "gui-update", "gui-accounts"],
    ("ITSUP", 13, 6): ["w11-processes", "w11-netsh"],
    ("NETOPS", 1, 2): ["win-ipconfig"],
    ("NETOPS", 2, 1): ["sw-vlan-access"],
    ("NETOPS", 2, 2): ["sw-vlan-access", "sw-trunk-basics"],
    ("NETOPS", 2, 4): ["sw-vlan-and-trunk"],
    ("NETOPS", 3, 1): ["rtr-gateway"],
    ("NETOPS", 3, 4): ["rtr-two-interfaces"],
    ("NETOPS", 4, 1): ["win-dhcp-renew"],
    ("NETOPS", 4, 2): ["win-dns-break"],
    ("NETOPS", 4, 4): ["win-full-triage"],
    ("NETOPS", 6, 4): ["win-full-triage", "sw-vlan-and-trunk", "rtr-edge-complete"],
    ("NETOPS", 9, 1): ["sw-vlan-access"],
    ("NETOPS", 9, 2): ["sw-vlan-access", "sw-trunk-basics", "sw-vlan-and-trunk"],
    ("NETOPS", 9, 3): ["rtr-gateway", "rtr-two-interfaces"],
    ("NETOPS", 9, 4): ["rtr-edge-complete"],
    ("NETOPS", 9, 5): ["sw-vlan-and-trunk", "rtr-edge-complete"],
    ("NETOPS", 9, 6): ["sw-hostname-write", "rtr-hostname-write"],
}

LAB_ALIGN = {
    "ticket-intake": "show ticket, classify, impact, escalate, note, submit — same order as Chapter 1.5.",
    "hw-board": "show board, then form-factor, socket, memory, storage, post, submit — Chapter 2.",
    "gui-about": "Click Settings → System → About. Read edition and device name.",
    "gui-ethernet": "Click Settings → Network & internet → Ethernet. Read IPv4, gateway, and DNS.",
    "gui-renew": "On Ethernet, Disconnect then Connect to recycle the lease.",
    "gui-services": "Open Services and confirm DHCP Client, DNS Client, and Defender are Running.",
    "w11-inventory": "On the Windows 11 VM run winver, systeminfo, whoami, and hostname before you change anything.",
    "w11-powershell-net": "Switch to PowerShell, then Get-NetIPConfiguration, Get-NetAdapter, Test-Connection 10.20.30.1.",
    "w11-services": "Get-Service Dhcp, Dnscache, and WinDefend — the services behind lease, cache, and Defender.",
    "win-ipconfig": "Practice reading hostname, IPv4, mask, gateway, and DNS with ipconfig /all.",
    "win-dns-break": "Prove IP works and the name fails: ping the IP, ping the name, nslookup, then flushdns.",
    "win-dhcp-renew": "Cycle the lease: ipconfig /release, /renew, then ping the gateway.",
    "win-full-triage": "Run the full client path: identity → ping IP → ping name → nslookup → flush → release/renew.",
    "sw-vlan-access": "From enable → conf t → vlan 20 → name → interface fa0/2 → switchport mode access → switchport access vlan 20.",
    "sw-trunk-basics": "On the uplink (fa0/1): switchport mode trunk, then show running-config.",
    "sw-vlan-and-trunk": "Build VLAN 20, an access port, and a trunk in one sitting.",
    "rtr-gateway": "Address Gi0/0 as 10.20.0.1/24, no shutdown, show ip interface brief, ping 10.20.0.10.",
    "rtr-two-interfaces": "Bring up Gi0/0 and Gi0/1 as two connected LANs.",
    "rtr-edge-complete": "Dual interfaces, show ip route, ping both hosts.",
}


def labs_for_lesson(module, lesson=None):
    if not module:
        return []
    course = getattr(module, "course", None)
    code = getattr(course, "code", None) or ""
    ch = getattr(module, "order", None)
    lo = getattr(lesson, "order", None) if lesson is not None else None
    ids = list(LESSON_LABS.get((code, ch, lo), []))
    if not ids and lesson is not None:
        title = (getattr(lesson, "title", "") or "").lower()
        if "vlan" in title or "access port" in title:
            ids = ["sw-vlan-access"]
        elif "trunk" in title:
            ids = ["sw-trunk-basics"]
        elif "dhcp" in title:
            ids = ["win-dhcp-renew"]
        elif "dns" in title or "name resolution" in title:
            ids = ["win-dns-break"]
        elif "routing" in title or "connected route" in title or "interface" in title and "router" in title:
            ids = ["rtr-gateway"]
    labs = [LABS_BY_ID[i] for i in ids if i in LABS_BY_ID]
    for lab in labs:
        lab["align"] = LAB_ALIGN.get(lab["id"], lab.get("blurb") or "")
    return labs


def list_labs():
    return [
        {
            "id": l["id"],
            "title": l["title"],
            "kind": l["kind"],
            "blurb": l["blurb"],
            "builds_on": l.get("builds_on") or [],
        }
        for l in LABS
    ]


def get_lab(lab_id):
    return LABS_BY_ID.get(lab_id)


def fresh_state(lab_id):
    lab = get_lab(lab_id)
    if not lab:
        return None
    return deepcopy(lab["initial_state"])


def prompt_for(lab, state):
    kind = lab["kind"]
    host = state.get("hostname", "device")
    mode = state.get("mode", "user")
    if kind == "ticket":
        return "TICKET-DESK>"
    if kind == "windows":
        if (state.get("shell") or "cmd") == "ps":
            return "PS C:\\Users\\Trainee>"
        return "C:\\Users\\Trainee>"
    if mode == "user":
        return f"{host}>"
    if mode == "priv":
        return f"{host}#"
    if mode == "config":
        return f"{host}(config)#"
    if mode == "config-if":
        return f"{host}(config-if)#"
    if mode == "config-vlan":
        return f"{host}(config-vlan)#"
    return f"{host}>"


def _mark(done, oid):
    if oid not in done:
        done.append(oid)


def _is_conf_t(cl):
    # Require the terminal keyword — "conf" / "configure" alone is incomplete
    return cl in (
        "configure terminal", "configure term", "configure t",
        "config terminal", "config term", "config t",
        "conf terminal", "conf term", "conf t",
    )


def _norm_sw(state):
    vlans = {}
    for k, v in (state.get("vlans") or {1: "default"}).items():
        try:
            vlans[int(k)] = v
        except (TypeError, ValueError):
            continue
    if 1 not in vlans:
        vlans[1] = "default"
    state["vlans"] = vlans
    for p, cfg in (state.get("interfaces") or {}).items():
        if isinstance(cfg, dict) and "vlan" in cfg:
            try:
                cfg["vlan"] = int(cfg["vlan"])
            except (TypeError, ValueError):
                cfg["vlan"] = 1
    if state.get("edit_vlan") is not None:
        try:
            state["edit_vlan"] = int(state["edit_vlan"])
        except (TypeError, ValueError):
            state["edit_vlan"] = None
    state.setdefault("mode", "user")
    return state


def _norm_if_sw(ifname, interfaces):
    import re
    raw = (ifname or "").strip()
    key = raw.lower().replace(" ", "")
    m = re.match(r"^(fa|f|fastethernet|gi|g|gigabitethernet)(\d+)/(\d+)$", key)
    if m:
        slot, port = m.group(2), m.group(3)
        kind = m.group(1)
        canon = f"GigabitEthernet{slot}/{port}" if kind in ("gi", "g", "gigabitethernet") else f"FastEthernet{slot}/{port}"
        if canon not in interfaces:
            interfaces[canon] = {"mode": "access", "vlan": 1, "up": True, "trunk": False}
        return canon
    for k in interfaces:
        if k.lower() == key or k.lower().replace(" ", "") == key:
            return k
    return raw


def _norm_if_rtr(ifname, interfaces):
    import re
    raw = (ifname or "").strip()
    key = raw.lower().replace(" ", "")
    m = re.match(r"^(gi|g|gigabitethernet|fa|f|fastethernet)(\d+)/(\d+)$", key)
    if m:
        slot, port = m.group(2), m.group(3)
        kind = m.group(1)
        canon = f"FastEthernet{slot}/{port}" if kind in ("fa", "f", "fastethernet") else f"GigabitEthernet{slot}/{port}"
        if canon not in interfaces:
            interfaces[canon] = {"ip": None, "mask": None, "up": False, "admin": False}
        return canon
    for k in interfaces:
        if k.lower() == key or k.lower().replace(" ", "") == key:
            return k
    return raw


# ── Windows ─────────────────────────────────────────────────────────

def run_windows(cmd, state, done):
    c = cmd.strip()
    cl = c.lower()
    out = []

    if cl in ("help", "?"):
        out.append("Windows 11 Training VM — Command Prompt and PowerShell")
        out.append("Identity:  hostname | whoami | winver | systeminfo | Get-ComputerInfo")
        out.append("Network:   ipconfig /all | Get-NetIPConfiguration | Get-NetAdapter")
        out.append("           ping | Test-Connection | nslookup | Resolve-DnsName | tracert")
        out.append("Lease:     ipconfig /release | ipconfig /renew | ipconfig /flushdns")
        out.append("Services:  Get-Service Dhcp | Get-Service Dnscache | Get-Service WinDefend")
        out.append("Shell:     powershell | cmd | cls")
        return out, state, done

    if cl in ("powershell", "pwsh"):
        state["shell"] = "ps"
        out.append("Windows PowerShell")
        out.append("Copyright (C) Microsoft Corporation. Training VM simulation.")
        _mark(done, "ps_shell")
        return out, state, done

    if cl == "cmd":
        state["shell"] = "cmd"
        out.append("Microsoft Windows [Version 10.0.22631.3737]")
        return out, state, done

    if cl in ("winver", "winver.exe"):
        out.append(f"{state.get('edition')}  Version {state.get('version')}  OS Build {state.get('build')}")
        out.append("CIWT Windows 11 Training VM — not a licensed Microsoft image.")
        _mark(done, "winver")
        return out, state, done

    if cl in ("get-computerinfo", "get-computerinfo | select windowsproductname,windowsversion,osbuildnumber"):
        out.append(f"WindowsProductName : {state.get('edition')}")
        out.append(f"WindowsVersion     : {state.get('version')}")
        out.append(f"OsBuildNumber      : {state.get('build')}")
        out.append(f"CsName             : {state.get('hostname')}")
        _mark(done, "winver")
        return out, state, done

    if cl == "whoami":
        out.append(state.get("user") or "CIWT\\Trainee")
        _mark(done, "whoami")
        return out, state, done

    if cl == "systeminfo":
        out.append("Host Name:                 " + state.get("hostname", ""))
        out.append("OS Name:                   " + state.get("edition", ""))
        out.append("OS Version:                10.0." + str(state.get("build")))
        out.append("System Type:               x64-based PC")
        out.append("Domain:                    " + state.get("domain", "TRAINING"))
        out.append("Network Card(s):           Ethernet  IPv4 " + str(state.get("ipv4")))
        _mark(done, "systeminfo")
        return out, state, done

    if cl in ("get-netipconfiguration", "get-netipconfiguration -detailed"):
        gw = "" if state.get("released") else state.get("gateway")
        out.append("InterfaceAlias       : Ethernet")
        out.append("InterfaceIndex       : 12")
        out.append("InterfaceDescription : Intel(R) Ethernet Connection")
        out.append("NetProfile.Name      : TRAINING")
        out.append("IPv4Address          : " + str(state.get("ipv4")))
        out.append("IPv4DefaultGateway   : " + str(gw or ""))
        out.append("DNSServer            : " + ", ".join(state.get("dns") or []))
        _mark(done, "netip")
        _mark(done, "run_ipconfig")
        return out, state, done

    if cl == "get-netadapter":
        out.append("Name      Status       MacAddress         LinkSpeed")
        out.append("----      ------       ----------         ---------")
        out.append("Ethernet  Up           00-1A-2B-AA-BB-07  1 Gbps")
        _mark(done, "netadapter")
        return out, state, done

    if cl.startswith("get-dnsclientserveraddress"):
        for d in state.get("dns") or []:
            out.append(f"Ethernet    2  {d}")
        return out, state, done

    if cl.startswith("resolve-dnsname "):
        name = c.split(None, 1)[1].strip()
        name_map = state.get("name_map") or {}
        resolved = None
        for k, v in name_map.items():
            if k.lower() == name.lower():
                resolved = v
        if resolved:
            out.append(f"Name     Type   TTL   Section    IPAddress")
            out.append(f"{name}  A      30    Answer     {resolved}")
        else:
            out.append(f"Resolve-DnsName : {name} : DNS name does not exist")
            _mark(done, "nslookup_fail")
        return out, state, done

    if cl.startswith("test-connection "):
        target = c.split()[-1]
        pingable = set(state.get("pingable_ips") or [])
        if target in pingable or target == state.get("gateway") or target == state.get("ipv4"):
            out.append("Source        Destination     Bytes Time(ms)")
            out.append(f"CIWT-W11-07   {target:<15} 32    1")
            _mark(done, "test_conn")
            if target in (state.get("gateway"), "10.20.30.1"):
                _mark(done, "ping_gw")
        else:
            out.append(f"Testing {target} failed: Request timed out")
        return out, state, done

    if cl.startswith("get-service"):
        name = "dhcp"
        parts = cl.split()
        if len(parts) >= 2:
            name = parts[1]
        svc_map = {k.lower(): (k, v) for k, v in (state.get("services") or {}).items()}
        hit = svc_map.get(name.lower())
        if hit:
            out.append("Status  Name       DisplayName")
            out.append("------  ----       -----------")
            out.append(f"{hit[1]:<7} {hit[0]:<10} {hit[0]}")
            if name.lower() == "dhcp":
                _mark(done, "svc_dhcp")
            if name.lower() == "dnscache":
                _mark(done, "svc_dns")
            if name.lower() == "windefend":
                _mark(done, "svc_def")
        else:
            out.append("Get-Service : Cannot find any service with service name '" + name + "'")
        return out, state, done

    if cl in ("get-localuser", "net user"):
        out.append("Name           Enabled")
        for u in state.get("users") or []:
            out.append(f"{u:<14} True")
        return out, state, done

    if cl in ("netsh interface ip show config", "netsh int ip show config", "netsh interface ip show address"):
        out.append("Configuration for interface \"Ethernet\"")
        out.append(f"    DHCP enabled:                         {str(state.get('dhcp')).capitalize()}")
        out.append(f"    IP Address:                           {state.get('ipv4')}")
        out.append(f"    Subnet Prefix:                        {state.get('mask')}")
        out.append(f"    Default Gateway:                      {'' if state.get('released') else state.get('gateway')}")
        for d in state.get("dns") or []:
            out.append(f"    DNS servers:                          {d}")
        _mark(done, "netsh")
        _mark(done, "run_ipconfig")
        return out, state, done

    if cl in ("tasklist", "tasklist /fo table"):
        out.append("Image Name                     PID Session Name        Mem Usage")
        out.append("System Idle Process              0 Services               8 K")
        out.append("csrss.exe                      712 Services           4,212 K")
        out.append("explorer.exe                  4312 Console           42,108 K")
        out.append("MsMpEng.exe                   2104 Services          88,000 K")
        _mark(done, "tasklist")
        return out, state, done

    if cl in ("get-process",):
        out.append("Handles  NPM(K)    PM(K)      WS(K)     CPU(s)   Id  ProcessName")
        out.append("    412      28    12000      42000       1.10 4312  explorer")
        out.append("    880      40    88000      91000       4.20 2104  MsMpEng")
        _mark(done, "get_process")
        return out, state, done

    if cl in ("sfc /scannow", "sfc"):
        out.append("Beginning system scan. This process will take some time.")
        out.append("Windows Resource Protection did not find any integrity violations.")
        return out, state, done

    if cl.startswith("gpupdate"):
        out.append("Updating policy...")
        out.append("Computer Policy update has completed successfully.")
        out.append("User Policy update has completed successfully.")
        return out, state, done

    if cl in ("netsh wlan show interfaces", "netsh wlan show interface"):
        out.append("There is 1 interface on the system:")
        out.append("    Name                   : Wi-Fi")
        out.append("    State                  : disconnected")
        out.append("    Radio                  : Hardware On")
        _mark(done, "wlan")
        return out, state, done

    if cl in ("netsh advfirewall show allprofiles", "netsh advfirewall show currentprofile"):
        out.append("Domain Profile Settings:")
        out.append("State                                 ON")
        out.append("Private Profile Settings:")
        out.append("State                                 ON")
        out.append("Public Profile Settings:")
        out.append("State                                 ON")
        _mark(done, "fw")
        return out, state, done

    if cl in ("list disk", "diskpart"):
        out.append("  Disk ###  Status         Size     Free     Dyn  Gpt")
        out.append("  Disk 0    Online          127 GB   1024 KB        *")
        out.append("  Disk 1    Online           20 GB      0 B")
        _mark(done, "listdisk")
        return out, state, done

    if cl == "hostname":
        out.append(state.get("hostname", "PC"))
        _mark(done, "run_hostname")
        return out, state, done

    if cl in ("ipconfig", "ipconfig /all"):
        out.append("")
        out.append("Windows IP Configuration")
        out.append("")
        out.append(f"   Host Name . . . . . . . . . . . . : {state.get('hostname')}")
        out.append("Ethernet adapter Ethernet:")
        out.append("")
        out.append(f"   IPv4 Address. . . . . . . . . . . : {state.get('ipv4')}")
        out.append(f"   Subnet Mask . . . . . . . . . . . : {state.get('mask')}")
        gw = "" if state.get("released") else state.get("gateway")
        out.append(f"   Default Gateway . . . . . . . . . : {gw or ''}")
        for i, d in enumerate(state.get("dns") or []):
            label = "   DNS Servers . . . . . . . . . . . :" if i == 0 else "                                       "
            out.append(f"{label} {d}")
        _mark(done, "run_ipconfig")
        return out, state, done

    if cl == "ipconfig /flushdns":
        state["dns_cache_flushed"] = True
        out.append("Successfully flushed the DNS Resolver Cache.")
        _mark(done, "flush_dns")
        return out, state, done

    if cl == "ipconfig /release":
        state["released"] = True
        state["ipv4_prev"] = state.get("ipv4")
        state["ipv4"] = "0.0.0.0"
        out.append("")
        out.append("Windows IP Configuration")
        out.append("")
        out.append("Ethernet adapter Ethernet:")
        out.append("")
        out.append("   IPv4 Address. . . . . . . . . . . : 0.0.0.0")
        out.append("   Subnet Mask . . . . . . . . . . . : 0.0.0.0")
        out.append("   Default Gateway . . . . . . . . . :")
        _mark(done, "release")
        return out, state, done

    if cl == "ipconfig /renew":
        state["released"] = False
        state["ipv4"] = state.get("ipv4_prev") or "10.20.30.47"
        out.append("")
        out.append("Windows IP Configuration")
        out.append("")
        out.append("Ethernet adapter Ethernet:")
        out.append("")
        out.append(f"   IPv4 Address. . . . . . . . . . . : {state.get('ipv4')}")
        out.append(f"   Subnet Mask . . . . . . . . . . . : {state.get('mask')}")
        out.append(f"   Default Gateway . . . . . . . . . : {state.get('gateway')}")
        _mark(done, "renew")
        return out, state, done

    if cl.startswith("ping "):
        parts = c.split()
        target = parts[-1]
        pingable = set(state.get("pingable_ips") or [])
        name_map = state.get("name_map")
        # name targets
        if any(ch.isalpha() for ch in target):
            resolved = None
            if isinstance(name_map, dict):
                for k, v in name_map.items():
                    if k.lower() == target.lower():
                        resolved = v
                        break
            if resolved:
                out.append(f"Pinging {target} [{resolved}] with 32 bytes of data:")
                out.append(f"Reply from {resolved}: bytes=32 time=1ms TTL=64")
                out.append("Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)")
            else:
                out.append(f"Ping request could not find host {target}. Please check the name and try again.")
                _mark(done, "ping_name_fail")
            return out, state, done
        if target in ("127.0.0.1", "localhost"):
            out.append(f"Pinging {target} with 32 bytes of data:")
            out.append("Reply from 127.0.0.1: bytes=32 time<1ms TTL=128")
            out.append("Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)")
            _mark(done, "ping_loop")
            return out, state, done
        if target in pingable or target == state.get("ipv4") or target == state.get("gateway"):
            out.append(f"Pinging {target} with 32 bytes of data:")
            out.append(f"Reply from {target}: bytes=32 time<1ms TTL=64")
            out.append(f"Reply from {target}: bytes=32 time<1ms TTL=64")
            out.append("Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)")
            if target == "10.20.30.50":
                _mark(done, "ping_ip_ok")
            if target == state.get("gateway") or target == "10.20.30.1":
                _mark(done, "ping_gw")
        else:
            out.append(f"Pinging {target} with 32 bytes of data:")
            out.append("Request timed out.")
            out.append("Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)")
        return out, state, done

    if cl.startswith("nslookup "):
        name = c.split(None, 1)[1].strip()
        name_map = state.get("name_map")
        dns = (state.get("dns") or ["0.0.0.0"])[0]
        out.append("Server:  dns-lab.training.local")
        out.append(f"Address:  {dns}")
        out.append("")
        resolved = None
        if isinstance(name_map, dict):
            for k, v in name_map.items():
                if k.lower() == name.lower():
                    resolved = v
                    break
        if isinstance(name_map, dict) and resolved is None:
            out.append(f"*** dns-lab.training.local can't find {name}: Non-existent domain")
            _mark(done, "nslookup_fail")
        elif resolved:
            out.append(f"Name:    {name}")
            out.append(f"Address:  {resolved}")
            _mark(done, "ns_ok")
        else:
            out.append(f"Name:    {name}")
            out.append("Address:  10.20.30.50")
            _mark(done, "ns_ok")
        return out, state, done

    if cl in ("arp -a", "arp"):
        gw = state.get("gateway") or "10.20.30.1"
        out.append("Interface: Ethernet")
        out.append("  Internet Address      Physical Address      Type")
        out.append(f"  {gw}           00-1a-2b-3c-4d-01     dynamic")
        out.append(f"  {state.get('ipv4')}        00-1a-2b-aa-bb-07     static")
        _mark(done, "arp")
        return out, state, done

    if cl.startswith("tracert ") or cl.startswith("traceroute "):
        target = c.split(None, 1)[1].strip()
        out.append(f"Tracing route to {target}")
        out.append(f"  1    <1 ms    <1 ms    <1 ms  {state.get('gateway')}")
        pingable = set(state.get("pingable_ips") or [])
        if target in pingable or target.replace(".", "").isdigit():
            out.append(f"  2    1 ms     1 ms     1 ms  {target}")
        out.append("Trace complete.")
        return out, state, done

    if cl in ("route print", "route"):
        out.append("IPv4 Route Table")
        out.append(f"  0.0.0.0          0.0.0.0    {state.get('gateway')}    {state.get('ipv4')}")
        out.append(f"  {'.'.join((state.get('ipv4') or '10.20.30.47').split('.')[:3])}.0    255.255.255.0    On-link    {state.get('ipv4')}")
        _mark(done, "route")
        return out, state, done

    if cl in ("netstat", "netstat -an", "netstat -a"):
        out.append("Active Connections")
        out.append("  Proto  Local Address          Foreign Address        State")
        out.append(f"  TCP    {state.get('ipv4')}:49712      10.20.30.10:53          TIME_WAIT")
        _mark(done, "netstat")
        return out, state, done

    if cl == "getmac":
        out.append("Physical Address    Transport Name")
        out.append("00-1A-2B-AA-BB-07   Ethernet")
        _mark(done, "getmac")
        return out, state, done

    if cl == "ipconfig /displaydns":
        out.append("Windows IP Configuration")
        if state.get("dns_cache_flushed"):
            out.append("    (cache empty)")
        else:
            out.append("    gateway.training.local")
            out.append("        Record Name . . . : gateway.training.local")
            out.append("        A (Host) Record . : 10.20.30.1")
        return out, state, done

    if cl.startswith("ping ") is False and cl == "ping":
        out.append("Usage: ping [-n count] target")
        return out, state, done

    out.append(f"'{c}' is not recognized as an internal or external command,")
    out.append("operable program or batch file.")
    return out, state, done


# ── Switch ──────────────────────────────────────────────────────────

def run_switch(cmd, state, done):
    state = _norm_sw(state)
    c = cmd.strip()
    cl = c.lower().strip()
    if cl.startswith("do "):
        cl = cl[3:].strip()
        c = c[3:].strip()
    mode = state.get("mode", "user")
    out = []

    if cl in ("help", "?"):
        out.append("Exec: enable | exit | end | show ... | ping")
        out.append("Config: configure terminal | vlan | interface | hostname")
        out.append("If: switchport mode access|trunk | switchport access vlan | no shutdown")
        return out, state, done

    if cl == "enable":
        if mode not in ("user", "priv"):
            out.append("% Invalid input detected at '^' marker.")
            return out, state, done
        state["mode"] = "priv"
        state["prompt_if"] = None
        _mark(done, "enable")
        return out, state, done

    if _is_conf_t(cl):
        if mode != "priv":
            out.append("% Invalid input detected at '^' marker.")
            return out, state, done
        state["mode"] = "config"
        state["prompt_if"] = None
        return out, state, done

    if cl == "end":
        state["mode"] = "priv"
        state["prompt_if"] = None
        state["edit_vlan"] = None
        return out, state, done

    if cl == "exit":
        if mode == "config-if":
            state["mode"] = "config"
            state["prompt_if"] = None
        elif mode == "config-vlan":
            state["mode"] = "config"
            state["edit_vlan"] = None
        elif mode == "config":
            state["mode"] = "priv"
        elif mode == "priv":
            state["mode"] = "user"
        return out, state, done

    if mode == "config" and cl.startswith("hostname "):
        state["hostname"] = c.split(None, 1)[1].strip()
        _mark(done, "hostname")
        return out, state, done

    if mode == "config" and cl.startswith("banner "):
        state["banner"] = c
        _mark(done, "banner")
        return out, state, done

    if cl.startswith("vlan "):
        if mode not in ("config", "config-vlan"):
            out.append("% Invalid input detected at '^' marker.")
            return out, state, done
        parts = c.split()
        if len(parts) < 2:
            out.append("% Incomplete command. Example: vlan 20")
            return out, state, done
        try:
            vid = int(parts[1])
        except Exception:
            out.append("% Invalid VLAN id. Example: vlan 20")
            return out, state, done
        if vid < 1 or vid > 4094:
            out.append("% Invalid VLAN id (1-4094)")
            return out, state, done
        state["vlans"][vid] = state["vlans"].get(vid) or f"VLAN{vid:04d}"
        state["mode"] = "config-vlan"
        state["edit_vlan"] = vid
        if vid == 20:
            _mark(done, "vlan20")
        return out, state, done

    if mode == "config-vlan" and cl.startswith("name "):
        name = c.split(None, 1)[1].strip()
        vid = int(state.get("edit_vlan") or 0)
        state["vlans"][vid] = name
        if vid == 20:
            _mark(done, "vlan20")
        return out, state, done

    if cl.startswith("interface "):
        if mode not in ("config", "config-if", "config-vlan"):
            out.append("% Requires configure terminal first.")
            return out, state, done
        ifname = _norm_if_sw(c.split(None, 1)[1], state["interfaces"])
        if ifname not in state["interfaces"]:
            out.append("% Invalid interface")
            return out, state, done
        state["mode"] = "config-if"
        state["prompt_if"] = ifname
        state["edit_vlan"] = None
        return out, state, done

    if mode == "config-if":
        ifn = state.get("prompt_if")
        iface = state["interfaces"].setdefault(ifn, {"mode": "access", "vlan": 1, "up": True})
        if cl in ("switchport mode access", "sw mode access"):
            iface["mode"] = "access"
            iface["trunk"] = False
            state["interfaces"][ifn] = iface
            return out, state, done
        if cl in ("switchport mode trunk", "sw mode trunk"):
            iface["mode"] = "trunk"
            iface["trunk"] = True
            state["interfaces"][ifn] = iface
            if "0/1" in str(ifn):
                _mark(done, "trunk")
            return out, state, done
        if cl.startswith("switchport access vlan ") or cl.startswith("sw access vlan "):
            try:
                vid = int(c.split()[-1])
            except Exception:
                out.append("% Example: switchport access vlan 20")
                return out, state, done
            iface["vlan"] = vid
            iface["mode"] = "access"
            state["interfaces"][ifn] = iface
            state["vlans"].setdefault(vid, f"VLAN{vid:04d}")
            if "0/2" in str(ifn) and vid == 20:
                _mark(done, "access")
            return out, state, done
        if cl == "no shutdown":
            iface["up"] = True
            state["interfaces"][ifn] = iface
            return out, state, done
        if cl == "shutdown":
            iface["up"] = False
            state["interfaces"][ifn] = iface
            return out, state, done
        if cl.startswith("description ") or cl.startswith("speed ") or cl.startswith("duplex "):
            if cl.startswith("description "):
                _mark(done, "desc")
            return out, state, done
        if cl.startswith("switchport trunk allowed vlan") or cl == "switchport nonegotiate":
            return out, state, done
        if cl.startswith("switchport port-security"):
            iface["portsec"] = True
            state["interfaces"][ifn] = iface
            _mark(done, "portsec")
            return out, state, done

    if cl in ("show vlan brief", "sh vlan brief", "show vlan", "sh vlan"):
        out.append("VLAN Name                             Status    Ports")
        out.append("---- -------------------------------- --------- -------------------------------")
        for vid, name in sorted(state["vlans"].items(), key=lambda x: int(x[0])):
            ports = [p for p, cfg in state["interfaces"].items() if int(cfg.get("vlan") or 0) == int(vid)]
            short = ",".join(p.replace("FastEthernet", "Fa") for p in ports)
            out.append(f"{int(vid):<4} {name:<32} active    {short}")
        if 20 in state["vlans"] and any(int(cfg.get("vlan") or 0) == 20 for cfg in state["interfaces"].values()):
            _mark(done, "verify")
        return out, state, done

    if cl in ("show interfaces status", "sh int status", "show interface status"):
        out.append("Port      Status       Vlan")
        for p, cfg in state["interfaces"].items():
            st = "connected" if cfg.get("up", True) else "disabled"
            vlan = "trunk" if cfg.get("mode") == "trunk" or cfg.get("trunk") else cfg.get("vlan")
            out.append(f"{p.replace('FastEthernet','Fa'):8} {st:12} {vlan}")
        _mark(done, "int_status")
        return out, state, done

    if cl in ("show running-config", "sh run", "show run"):
        out.append(f"hostname {state.get('hostname')}")
        for vid, name in sorted(state["vlans"].items(), key=lambda x: int(x[0])):
            if int(vid) == 1:
                continue
            out.append(f"vlan {vid}")
            out.append(f" name {name}")
        for p, cfg in state["interfaces"].items():
            out.append(f"interface {p}")
            out.append(f" switchport mode {cfg.get('mode') or 'access'}")
            if cfg.get("mode") == "trunk" or cfg.get("trunk"):
                _mark(done, "verify_trunk")
            else:
                out.append(f" switchport access vlan {cfg.get('vlan', 1)}")
        return out, state, done

    if cl in ("show version", "sh ver", "show ver"):
        out.append(f"{state.get('hostname')} uptime is 1 day, 4 hours")
        out.append("Cisco IOS Software, Switch Training Image")
        _mark(done, "show_ver")
        return out, state, done

    if cl in ("show mac address-table", "show mac address table", "sh mac address-table", "show mac"):
        out.append("Vlan    Mac Address       Type        Ports")
        out.append("----    -----------       --------    -----")
        out.append("   1    0011.2233.4455    DYNAMIC     Fa0/2")
        _mark(done, "show_mac")
        return out, state, done

    if cl in ("show ip interface brief", "sh ip int brief", "show ip int brief"):
        out.append("Interface              IP-Address      OK? Method Status                Protocol")
        for p, cfg in state["interfaces"].items():
            st = "up" if cfg.get("up", True) else "down"
            out.append(f"{p:<22} unassigned      YES unset  {st:<21} {st}")
        return out, state, done

    if cl in ("show interfaces", "show interface", "sh int"):
        for p, cfg in state["interfaces"].items():
            st = "up" if cfg.get("up", True) else "down"
            out.append(f"{p} is {st}, line protocol is {st}")
        return out, state, done

    if cl in ("copy running-config startup-config", "copy run start", "write memory", "write mem", "write"):
        state["startup"] = True
        out.append("Destination filename [startup-config]?")
        out.append("[OK]")
        _mark(done, "write")
        return out, state, done

    if cl.startswith("ping "):
        target = c.split(None, 1)[1].strip()
        out.append("Sending 5, 100-byte ICMP Echos")
        out.append("!!!!!")
        out.append(f"Success rate is 100 percent (5/5) to {target}")
        return out, state, done

    if mode == "config" and cl.startswith("ip default-gateway "):
        return out, state, done

    if mode == "config" and cl.startswith("no vlan "):
        try:
            vid = int(c.split()[-1])
            state["vlans"].pop(vid, None)
        except Exception:
            pass
        return out, state, done

    out.append("% Invalid input detected at '^' marker.")
    return out, state, done


# ── Router ──────────────────────────────────────────────────────────

def run_router(cmd, state, done):
    c = cmd.strip()
    cl = c.lower().strip()
    if cl.startswith("do "):
        cl = cl[3:].strip()
        c = c[3:].strip()
    mode = state.get("mode", "user")
    out = []

    if cl in ("help", "?"):
        out.append("Exec: enable | exit | end | show ip interface brief | show ip route | ping")
        out.append("Config: configure terminal | interface | ip address | no shutdown")
        return out, state, done

    if cl == "enable":
        if mode not in ("user", "priv"):
            out.append("% Invalid input detected at '^' marker.")
            return out, state, done
        state["mode"] = "priv"
        _mark(done, "enable")
        return out, state, done

    if _is_conf_t(cl):
        if mode != "priv":
            out.append("% Invalid input detected at '^' marker.")
            return out, state, done
        state["mode"] = "config"
        return out, state, done

    if cl == "end":
        state["mode"] = "priv"
        state["prompt_if"] = None
        return out, state, done

    if cl == "exit":
        if mode == "config-if":
            state["mode"] = "config"
            state["prompt_if"] = None
        elif mode == "config":
            state["mode"] = "priv"
        elif mode == "priv":
            state["mode"] = "user"
        return out, state, done

    if cl.startswith("interface "):
        if mode not in ("config", "config-if"):
            out.append("% Requires configure terminal first.")
            return out, state, done
        ifname = _norm_if_rtr(c.split(None, 1)[1], state["interfaces"])
        if ifname not in state["interfaces"]:
            out.append("% Invalid interface. Try: interface GigabitEthernet0/0")
            return out, state, done
        state["mode"] = "config-if"
        state["prompt_if"] = ifname
        return out, state, done

    if mode == "config-if":
        ifn = state["prompt_if"]
        iface = state["interfaces"][ifn]
        if cl.startswith("ip address "):
            parts = c.split()
            if len(parts) >= 4:
                iface["ip"] = parts[2]
                iface["mask"] = parts[3]
                state["interfaces"][ifn] = iface
                if ifn.endswith("0/0") and parts[2] == "10.20.0.1":
                    _mark(done, "addr")
                if ifn.endswith("0/1") and parts[2] == "10.30.0.1":
                    _mark(done, "addr2")
            else:
                out.append("% Example: ip address 10.20.0.1 255.255.255.0")
            return out, state, done
        if cl == "no shutdown":
            iface["admin"] = True
            iface["up"] = bool(iface.get("ip"))
            state["interfaces"][ifn] = iface
            if ifn.endswith("0/0") and iface.get("ip") == "10.20.0.1":
                _mark(done, "addr")
            if ifn.endswith("0/1") and iface.get("ip") == "10.30.0.1":
                _mark(done, "addr2")
            return out, state, done
        if cl.startswith("description ") or cl.startswith("bandwidth "):
            if cl.startswith("description "):
                _mark(done, "desc")
            return out, state, done
        if cl == "shutdown":
            iface["admin"] = False
            iface["up"] = False
            state["interfaces"][ifn] = iface
            return out, state, done

    if mode == "config" and cl.startswith("hostname "):
        state["hostname"] = c.split(None, 1)[1].strip()
        _mark(done, "hostname")
        return out, state, done

    if mode == "config" and cl.startswith("ip route "):
        state.setdefault("static", []).append(c)
        if "0.0.0.0" in cl:
            _mark(done, "defroute")
        return out, state, done

    if cl in ("show ip interface brief", "sh ip int brief", "sh ip interface brief"):
        out.append("Interface                  IP-Address      OK? Method Status                Protocol")
        for p, cfg in state["interfaces"].items():
            ip = cfg.get("ip") or "unassigned"
            status = "up" if cfg.get("up") else ("administratively down" if not cfg.get("admin") else "down")
            proto = "up" if cfg.get("up") else "down"
            out.append(f"{p:<26} {ip:<15} YES manual {status:<21} {proto}")
        g0 = state["interfaces"].get("GigabitEthernet0/0", {})
        g1 = state["interfaces"].get("GigabitEthernet0/1", {})
        if g0.get("ip") == "10.20.0.1" and g0.get("up"):
            _mark(done, "show_ip")
        if g0.get("ip") == "10.20.0.1" and g0.get("up") and g1.get("ip") == "10.30.0.1" and g1.get("up"):
            _mark(done, "show_ip")
        return out, state, done

    if cl in ("show ip route", "sh ip route"):
        out.append("Codes: C - connected")
        any_route = False
        for p, cfg in state["interfaces"].items():
            if cfg.get("up") and cfg.get("ip"):
                ip = cfg["ip"]
                net = ".".join(ip.split(".")[:3]) + ".0/24"
                out.append(f"C    {net} is directly connected, {p}")
                any_route = True
        for s in state.get("static") or []:
            parts = s.split()
            if len(parts) >= 5:
                out.append(f"S*   {parts[2]}/{parts[3]} via {parts[4]}")
                any_route = True
                if parts[2] == "0.0.0.0":
                    _mark(done, "defroute")
        if any_route:
            _mark(done, "show_route")
        else:
            out.append("  (no connected routes yet)")
        return out, state, done

    if cl.startswith("ping "):
        target = c.split(None, 1)[1].strip()
        any_up = any(cfg.get("up") and cfg.get("ip") for cfg in state["interfaces"].values())
        if not any_up:
            out.append("Type escape sequence to abort.")
            out.append(".....")
            out.append("Success rate is 0 percent (0/5)")
            out.append("% Interface appears down — configure IP and no shutdown first.")
            return out, state, done
        hosts = state.get("hosts") or {}
        if hosts.get(target):
            out.append("Type escape sequence to abort.")
            out.append(f"Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:")
            out.append("!!!!!")
            out.append("Success rate is 100 percent (5/5)")
            if target == "10.20.0.10":
                _mark(done, "ping_pc")
            if target == "10.30.0.20":
                _mark(done, "ping_pc2")
        else:
            out.append("Type escape sequence to abort.")
            out.append(f"Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:")
            out.append(".....")
            out.append("Success rate is 0 percent (0/5)")
        return out, state, done

    if cl.startswith("traceroute "):
        target = c.split(None, 1)[1].strip()
        out.append(f"Tracing the route to {target}")
        out.append("  1 10.20.0.10 4 msec 4 msec 4 msec")
        _mark(done, "trace")
        return out, state, done

    if cl in ("show version", "sh ver"):
        out.append(f"{state.get('hostname')} uptime is 2 days")
        out.append("Cisco IOS Software, Router Training Image")
        return out, state, done

    if cl in ("show interfaces", "show interface", "sh int"):
        for p, cfg in state["interfaces"].items():
            st = "up" if cfg.get("up") else "administratively down"
            out.append(f"{p} is {st}")
            if cfg.get("ip"):
                out.append(f"  Internet address is {cfg['ip']}/{cfg.get('mask')}")
        return out, state, done

    if cl in ("show running-config", "show run", "sh run"):
        out.append(f"hostname {state.get('hostname')}")
        for p, cfg in state["interfaces"].items():
            out.append(f"interface {p}")
            if cfg.get("ip"):
                out.append(f" ip address {cfg['ip']} {cfg.get('mask')}")
            out.append(" no shutdown" if cfg.get("admin") else " shutdown")
        return out, state, done

    if cl in ("copy running-config startup-config", "copy run start", "write memory", "write mem", "write"):
        out.append("Destination filename [startup-config]?")
        out.append("[OK]")
        _mark(done, "write")
        return out, state, done

    if cl in ("show arp", "sh arp"):
        out.append("Protocol  Address          Age (min)  Hardware Addr   Type   Interface")
        out.append("Internet  10.20.0.10              1   000c.29aa.0001  ARPA   GigabitEthernet0/0")
        return out, state, done

    out.append("% Invalid input detected at '^' marker.")
    return out, state, done


def complete_command(lab_id, partial, mode=None):
    lab = get_lab(lab_id)
    if not lab:
        return {"text": partial or "", "options": [], "beep": True}
    return complete_ios_line(partial or "", lab["kind"], mode=mode)


def run_hw(cmd, state, done):
    raw = (cmd or "").strip()
    cl = raw.lower()
    answers = state.get("answers") or {}
    guess = state.setdefault("guess", {})
    marks = {
        "form-factor": "form",
        "socket": "socket",
        "memory": "memory",
        "storage": "storage",
        "post": "post",
    }
    if cl in ("help", "?"):
        return [
            "Commands: help, show board,",
            "  form-factor atx | microatx | mini-itx",
            "  socket lga1700 | am5",
            "  memory ddr4 | ddr5",
            "  storage nvme | sata",
            "  post memory | display | power | ok",
            "  submit",
        ], state, done
    if cl in ("show board", "show", "board"):
        _mark(done, "showed")
        card = (state.get("card") or "").split("\n")
        return ["BENCH CARD:"] + card + ["", "Your answers: " + ", ".join(
            f"{k}={guess.get(k) or '—'}" for k in marks
        )], state, done
    for key in marks:
        prefix = key + " "
        if cl.startswith(prefix) or cl.startswith(key.replace("-", " ") + " "):
            val = cl.split(None, 1)[1].strip().replace(" ", "")
            aliases = {
                "micro-atx": "microatx", "matx": "microatx",
                "miniitx": "mini-itx", "itx": "mini-itx",
                "lga": "lga1700",
                "am4": "am5",
            }
            val = aliases.get(val, val)
            guess[key] = val
            if val == answers.get(key):
                _mark(done, marks[key])
                return [f"{key} recorded: {val} (matches the card)."], state, done
            return [f"{key} recorded: {val}. Does not match the card — look again."], state, done
    if cl == "submit":
        missing = [k for k, oid in marks.items() if oid not in done]
        if "showed" not in done:
            missing = ["show board"] + missing
        if missing:
            return ["Cannot submit. Still need correct: " + ", ".join(missing)], state, done
        _mark(done, "submitted")
        return ["Bench card submitted. Isolation order stays: power, POST, display, firmware, OS."], state, done
    return ["Not recognized. Type help."], state, done


def run_ticket(cmd, state, done):
    """Block 1 intake desk — commands match Chapter 1.5."""
    raw = (cmd or "").strip()
    cl = raw.lower()
    if cl in ("help", "?"):
        return [
            "Commands:",
            "  help",
            "  show ticket",
            "  classify break-fix | request | incident",
            "  impact 1 | impact many",
            "  escalate yes | escalate no",
            "  note <symptom, observation, next step>",
            "  submit",
        ], state, done
    if cl in ("show ticket", "show", "ticket"):
        _mark(done, "showed")
        return [
            "RAW USER TEXT:",
            state.get("ticket") or "(empty)",
            "",
            "STATUS  classify=%s  impact=%s  escalate=%s" % (
                state.get("classify") or "—",
                state.get("impact") or "—",
                state.get("escalate") if state.get("escalate") is not None else "—",
            ),
            "NOTE    " + (state.get("note") or "(none)"),
        ], state, done
    if cl.startswith("classify "):
        val = cl.split(None, 1)[1].strip().replace("_", "-")
        aliases = {
            "break-fix": "break-fix", "breakfix": "break-fix", "break": "break-fix",
            "request": "request", "service": "request", "service-request": "request",
            "incident": "incident", "security": "incident",
        }
        if val not in aliases:
            return ["Unknown type. Use classify break-fix | request | incident"], state, done
        state["classify"] = aliases[val]
        _mark(done, "classified")
        return ["Classified as %s." % state["classify"]], state, done
    if cl.startswith("impact "):
        val = cl.split(None, 1)[1].strip()
        if val in ("1", "one", "single"):
            state["impact"] = "1"
        elif val in ("many", "multi", "multiple"):
            state["impact"] = "many"
        else:
            return ["Use impact 1 or impact many"], state, done
        _mark(done, "impact")
        return ["Impact set to %s." % state["impact"]], state, done
    if cl.startswith("escalate "):
        val = cl.split(None, 1)[1].strip()
        if val in ("yes", "y"):
            state["escalate"] = "yes"
        elif val in ("no", "n"):
            state["escalate"] = "no"
        else:
            return ["Use escalate yes or escalate no"], state, done
        _mark(done, "escalated")
        return ["Escalate = %s." % state["escalate"]], state, done
    if cl == "note" or cl.startswith("note "):
        text = raw.split(None, 1)[1].strip() if " " in raw else ""
        if len(text) < 24:
            return ["Note too short. Include symptom, one observation, and a next step."], state, done
        state["note"] = text
        _mark(done, "noted")
        return ["Note saved (%d characters)." % len(text)], state, done
    if cl == "submit":
        missing = []
        if not state.get("classify"):
            missing.append("classify")
        if not state.get("impact"):
            missing.append("impact")
        if state.get("escalate") not in ("yes", "no"):
            missing.append("escalate")
        if len(state.get("note") or "") < 24:
            missing.append("note")
        if missing:
            return ["Cannot submit. Still need: " + ", ".join(missing)], state, done
        _mark(done, "submitted")
        return [
            "Intake submitted.",
            "type=%s  impact=%s  escalate=%s" % (state["classify"], state["impact"], state["escalate"]),
            "note: " + state["note"],
        ], state, done
    return ["Not recognized. Type help."], state, done


def run_command(lab_id, state, done, command):
    lab = get_lab(lab_id)
    if not lab:
        return {"error": "Unknown lab"}, state, done
    done = list(done or [])
    state = deepcopy(state) if state else fresh_state(lab_id)
    cmd = (command or "").strip()
    if not cmd:
        return {"lines": [], "prompt": prompt_for(lab, state), "done": done, "complete": False}, state, done
    if cmd.lower() in ("clear", "cls"):
        return {
            "lines": [], "clear": True, "prompt": prompt_for(lab, state),
            "done": done, "complete": _complete(lab, done),
        }, state, done

    if lab["kind"] in ("switch", "router") and (cmd.strip() == "?" or cmd.strip().endswith("?") or cmd.strip().lower() == "help"):
        help_lines = ios_help(lab["kind"], state.get("mode") or "user", cmd)
        return {
            "lines": help_lines,
            "prompt": prompt_for(lab, state),
            "done": done,
            "complete": _complete(lab, done),
        }, state, done

    if lab["kind"] in ("switch", "router"):
        expanded, err = expand_ios_line(cmd, lab["kind"], mode=state.get("mode") or "user")
        if err:
            return {
                "lines": err,
                "prompt": prompt_for(lab, state),
                "done": done,
                "complete": _complete(lab, done),
            }, state, done
        cmd = expanded or cmd

    if lab["kind"] == "ticket":
        if lab_id == "hw-board" or (state or {}).get("kind") == "hw":
            lines, state, done = run_hw(cmd, state, done)
        else:
            lines, state, done = run_ticket(cmd, state, done)
    elif lab["kind"] == "windows":
        lines, state, done = run_windows(cmd, state, done)
    elif lab["kind"] == "switch":
        lines, state, done = run_switch(cmd, state, done)
    else:
        lines, state, done = run_router(cmd, state, done)

    complete = _complete(lab, done)
    return {
        "lines": lines,
        "prompt": prompt_for(lab, state),
        "done": done,
        "complete": complete,
        "success_msg": lab["success_msg"] if complete else None,
    }, state, done


def _complete(lab, done):
    needed = {o["id"] for o in lab["objectives"]}
    return needed.issubset(set(done or []))


def verify_all_labs():
    """Run every VERIFY_SEQUENCES path. Returns (ok: bool, report: list[str])."""
    report = []
    ok = True
    for lab_id, (cmds, expect) in VERIFY_SEQUENCES.items():
        state = fresh_state(lab_id)
        done = []
        failed_cmd = None
        for cmd in cmds:
            result, state, done = run_command(lab_id, state, done, cmd)
            lines = result.get("lines") or []
            if any(
                ("Incomplete" in ln or "not recognized" in ln or "requires global" in ln.lower())
                for ln in lines
            ):
                # only fail if we expected success on a required step
                if "requires" in " ".join(lines).lower() and cmd.startswith("vlan"):
                    failed_cmd = cmd
                    break
        missing = set(expect) - set(done)
        if missing or failed_cmd:
            ok = False
            report.append(f"FAIL {lab_id}: missing={missing or '-'} failed_cmd={failed_cmd or '-'} done={done}")
        else:
            report.append(f"PASS {lab_id}")

    # Abbreviation / unique-prefix path (Cisco-style)
    abbr = [
        ("sw-vlan-access", [
            "en", "conf t", "vl 20", "na TRAINING-USERS",
            "int fa0/2", "sw mo ac", "sw ac vl 20", "end", "sh vlan br",
        ], ["enable", "vlan20", "access", "verify"]),
        ("rtr-gateway", [
            "en", "conf t", "int gi0/0", "ip add 10.20.0.1 255.255.255.0",
            "no sh", "end", "sh ip int br", "ping 10.20.0.10",
        ], ["enable", "addr", "show_ip", "ping_pc"]),
    ]
    for lab_id, cmds, expect in abbr:
        state = fresh_state(lab_id)
        done = []
        for cmd in cmds:
            result, state, done = run_command(lab_id, state, done, cmd)
        missing = set(expect) - set(done)
        if missing:
            ok = False
            report.append(f"FAIL {lab_id} abbreviations: missing={missing} done={done}")
        else:
            report.append(f"PASS {lab_id} abbreviations")
    return ok, report


if __name__ == "__main__":
    passed, lines = verify_all_labs()
    for ln in lines:
        print(ln)
    raise SystemExit(0 if passed else 1)
