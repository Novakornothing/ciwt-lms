# Real environments vs simulated labs

Status 18 Oct 2026, `labs` branch. Image, licences and measurements are in `docs/VM_IMAGE.md`.

## Summary

- **Real by default for Linux.**
  - Five labs run on genuine Linux machines that boot in the student's browser (v86 → WebAssembly). One of
    them runs two machines.
  - They are graded by reading the VM's real state:
    - files, modes and owners
    - users
    - running processes
    - init-script status
    - crontab
    - syslog
    - addresses, routes, `ip_forward` and `/etc/hosts`
    - live `ping` results
  - Grading also uses the virtual network's own evidence (DHCP ACK, DNS query) and the ordered command history.
  - There is no server cost and no per-student VM to manage. Everything works offline once the files are cached.
- **The simulated version stays as a fallback.** Every real lab names one (`fallback`). Its page links to the
  fallback and recommends it automatically when the device is weak: under 2 GB of reported memory, no
  WebAssembly, or a boot over 45 s. Each simulator page in turn links to its real twin.
- **Networking is real between machines.** The VMs' kernels really do the ARP, routing, forwarding, TTL decrement,
  DHCP client, resolver and traceroute. A small services host in the page answers as the DHCP server, DNS server,
  gateway and fileserver (`static/js/lab-vmnet.js`). The Packets tab shows every frame.
- **Windows and Cisco IOS stay high-fidelity simulations.** See "Windows" below.

## Labs: real vs simulated

| # | Lab | Kind | Environment |
|---|---|---|---|
| 1 | `win-ipconfig` — 1. Windows 11 VM — Read Network Identity | windows | Simulated |
| 2 | `win-dns-break` — 2. Windows 11 VM — DNS Failure Isolation | windows | Simulated — real twin: `linux-vm-netclient` |
| 3 | `win-dhcp-renew` — 3. Windows 11 VM — DHCP Release / Renew | windows | Simulated — real twin: `linux-vm-netclient` |
| 4 | `win-full-triage` — 4. Windows 11 VM — Full Client Triage | windows | Simulated |
| 5 | `w11-inventory` — 5. Windows 11 VM — Inventory the Endpoint | windows | Simulated |
| 6 | `w11-powershell-net` — 6. Windows 11 VM — PowerShell Network View | windows | Simulated |
| 7 | `w11-services` — 7. Windows 11 VM — Service Health | windows | Simulated |
| 8 | `w11-netsh` — 7b. Windows 11 VM — netsh interface view | windows | Simulated |
| 9 | `w11-processes` — 7c. Windows 11 VM — What's running | windows | Simulated |
| 10 | `gui-about` — 8. Windows 11 GUI — Settings About | win11gui | Simulated |
| 11 | `gui-ethernet` — 9. Windows 11 GUI — Ethernet properties | win11gui | Simulated |
| 12 | `gui-renew` — 10. Windows 11 GUI — Renew the Ethernet lease | win11gui | Simulated |
| 13 | `gui-services` — 11. Windows 11 GUI — Services | win11gui | Simulated |
| 14 | `gui-update` — 12. Windows 11 GUI — Windows Update | win11gui | Simulated |
| 15 | `gui-accounts` — 13. Windows 11 GUI — Accounts | win11gui | Simulated |
| 16 | `sw-vlan-access` — 5. Switch — VLAN + Access Port | switch | Simulated |
| 17 | `sw-trunk-basics` — 6. Switch — Trunk Uplink | switch | Simulated |
| 18 | `sw-vlan-and-trunk` — 7. Switch — VLAN + Access + Trunk (capstone) | switch | Simulated |
| 19 | `rtr-gateway` — 8. Router — Gateway Address + Ping | router | Simulated |
| 20 | `rtr-two-interfaces` — 9. Router — Two Connected Networks | router | Simulated — real twin: `linux-vm-routing` |
| 21 | `rtr-edge-complete` — 10. Router — Edge Complete (capstone) | router | Simulated |
| 22 | `sw-hostname-write` — 11. Switch — Hostname and save | switch | Simulated |
| 23 | `rtr-hostname-write` — 12. Router — Hostname and save | router | Simulated |
| 24 | `w11-firewall` — Windows 11 VM — Firewall profiles | windows | Simulated |
| 25 | `w11-disk` — Windows 11 VM — List disks | windows | Simulated |
| 26 | `gui-devices` — Windows 11 GUI — Device Manager | win11gui | Simulated |
| 27 | `sw-port-security` — Switch — Port security on an access port | switch | Simulated |
| 28 | `rtr-default-route` — Router — Default route to the WAN | router | Simulated — real twin: `linux-vm-routing` |
| 29 | `sw-banner` — Switch — Login banner | switch | Simulated |
| 30 | `w11-wlan` — Windows 11 VM — WLAN report | windows | Simulated |
| 31 | `sw-mac-table` — Switch — MAC address table | switch | Simulated |
| 32 | `rtr-describe` — Router — Interface description | router | Simulated |
| 33 | `win-arp` — Windows 11 VM — ARP cache | windows | Simulated |
| 34 | `sw-int-status` — Switch — Interface status | switch | Simulated |
| 35 | `rtr-trace` — Router — Traceroute | router | Simulated |
| 36 | `win-route` — Windows 11 VM — Route table | windows | Simulated |
| 37 | `win-getmac` — Windows 11 VM — MAC address | windows | Simulated |
| 38 | `win-netstat` — Windows 11 VM — Active connections | windows | Simulated |
| 39 | `win-hostname` — Windows 11 VM — Hostname | windows | Simulated |
| 40 | `win-ping-loop` — Windows 11 VM — Loopback ping | windows | Simulated |
| 41 | `win-nslookup-ok` — Windows 11 VM — Working name lookup | windows | Simulated |
| 42 | `win-flushdns` — Windows 11 VM — Flush DNS cache | windows | Simulated |
| 43 | `sw-show-ver` — Switch — show version | switch | Simulated |
| 44 | `sw-describe` — Switch — Access port description | switch | Simulated |
| 45 | `ticket-intake` — Block 1 — Ticket intake desk | ticket | Simulated |
| 46 | `hw-board` — Block 2 — Identify the board on the bench | ticket | Simulated |
| 47 | `net-subnet` — Subnetting workbench — calculate, size and validate | activity | Simulated |
| 48 | `hw-cables` — Connector and cable identification bench | activity | Simulated |
| 49 | `hw-pc-build` — Workstation build — pick compatible parts | activity | Simulated |
| 50 | `ticket-method` — Troubleshooting methodology — work a ticket end to end | activity | Simulated |
| 51 | `win-net-cli` — Windows CLI — isolate a name-resolution fault | windows | Simulated |
| 52 | `linux-shell` — Linux shell — files, permissions and logs | linux | Simulated — real twin: `linux-vm-perms`, `linux-vm-shell`, `linux-vm-services` |
| 53 | `print-trouble` — PowerShell — clear a stuck print queue | windows | Simulated |
| 54 | `rtr-vlan-acl` — Router — inter-VLAN routing and a guest ACL | router | Simulated |
| 55 | `sw-vlan-multi` — Switch — two VLANs, access ports and a pruned trunk | switch | Simulated |
| 56 | `wifi-secure` — SOHO router — secure the admin page, Wi-Fi and guest network | activity | Simulated |
| 57 | `sec-malware` — Malware response — the seven-step removal process | activity | Simulated |
| 58 | `ops-backup` — Backup and recovery — types, restore sets, 3-2-1, RPO/RTO | activity | Simulated |
| 59 | `virt-vm` — Virtualization — build a Windows 11 lab VM | activity | Simulated |
| 60 | `mob-mdm` — Mobile devices — connectivity and MDM tickets inside policy | activity | Simulated |
| 61 | `win-ad-users` — Active Directory Users and Computers — onboard, unlock, offboard | win11gui | Simulated |
| 62 | `win-laptop-ports` — Windows CLI — battery health, VM check, MX records and port tests | windows | Simulated |
| 63 | `win-wifi-survey` — Windows CLI — Wi-Fi survey on a laptop (signal, band, channel) | windows | Simulated |
| 64 | `hv-vswitch` — Hyper-V host — isolated virtual switch and checkpoints (PowerShell) | windows | Simulated |
| 65 | `linux-vm-perms` — Real Linux VM — files, ownership, permissions and a support script | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 66 | `linux-vm-shell` — Real Linux VM — shell basics: files, permissions, scripts and logs | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 67 | `linux-vm-services` — Real Linux VM — services, processes, a filling disk, cron and syslog | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 68 | `linux-vm-netclient` — Real Linux VM — lease, gateway and name resolution on a live network | vm | **Real** — 1 Linux VM in the browser + virtual network (DHCP/DNS host); fallback: `win-dhcp-renew`, `win-dns-break` |
| 69 | `linux-vm-routing` — Real Linux VMs — route between two networks (two machines, one router) | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `rtr-two-interfaces`, `rtr-default-route` |
| – | `CL-4` — Print path and laptop FRU identification | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-6` — Build, snapshot and network a virtual machine | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-7` — Structured troubleshooting drills on staged faults | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-8` — Windows recovery ladder in a lab VM | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-9` — Linux command line and permissions | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-10` — Endpoint security posture check and incident tabletop | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-11` — Slow PC: resource tools and clean-boot isolation | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-12` — Change request and recovery drill | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-13` — PowerShell evidence and name-resolution repair | classroom | **In class** — real equipment or lab VMs, instructor sign-off |

**Real environment: 5 labs** (`linux-vm-perms`, `linux-vm-shell`, `linux-vm-services`, `linux-vm-netclient`,
`linux-vm-routing`), plus the classroom labs CL-4…CL-13, which are done on real equipment or lab VMs and signed off
by the instructor.

**Simulated: 64 labs.** Of these, 5 have a real twin: `linux-shell`, `win-dhcp-renew`, `win-dns-break`,
`rtr-two-interfaces` and `rtr-default-route`.

## What each real lab checks inside the machine

| Lab | Machine state read by the probe | Network / history evidence |
|---|---|---|
| linux-vm-perms | directory exists, file content, mode `-rw-r-----`, user `tech1` exists and owns the file, `check.sh` is executable and prints `disk ok` when run | `ls -l` after `chmod` |
| linux-vm-shell | `logs/` and `notes.txt` exist, `backup.sh` has the owner x bit **and really ran** (its marker in `/tmp/backup`), report.txt others-r removed | `whoami`/`hostname`, `cd` then `ls -l`, `grep ERROR app.log` |
| linux-vm-services | runaway `debugdump` is no longer in `ps`; `/tmp` space freed; the init script is executable with the correct `DAEMON=`; `S50heartbeat status` says running and the log grows; root's crontab has `*/15 … cleanup.sh`; `SR-4201` is in `/var/log/messages` | investigated (`df`/`du`, then `ps`/`fuser`) before acting; status checked after start |
| linux-vm-netclient | eth0 holds a 10.10.0.100–150 lease; default route via 10.10.0.1; `nameserver 10.10.0.53`; the stale `/etc/hosts` line is gone; `ping intranet.ciwt.lab` really reaches 10.10.0.80 | the DHCP server sent an ACK (a hand-typed address does not count); the gateway saw a ping; the DNS server saw the query; `ip a` before `udhcpc`; `ip neigh` |
| linux-vm-routing | pc-a 10.1.0.10/24 and default via 10.1.0.1; rtr-1 has 10.1.0.1/24 + 10.2.0.1/24 and `ip_forward=1`; pc-a's live ping to 10.2.0.10 returns with **TTL 63**, so it was really routed | the fault was isolated (ping from the PC, then from the router) *before* forwarding was enabled; traceroute run on pc-a |

**How the grading works and what it trusts.**

- The probe is generated on the server from the lab's `vm_checks`. Each check runs under a watchdog.
- The probe carries a per-attempt nonce and the machine name. A forged nonce, or the other machine's result, is
  refused.
- The VMs run on the student's device, so a determined student could forge results. The labs are therefore
  formative. For summative use, pair them with the event log that the instructor sees, which records every line
  typed with its machine, or with a sign-off.

## Networking labs: what was evaluated

| Option | Verdict |
|---|---|
| Network namespaces / veth / bridge inside one VM | **Not possible with this image.** Tested: `ip netns` is absent from BusyBox `ip`; veth, bridge, dummy and VLAN all return "Operation not supported"; there is no `unshare`. It needs the institution image in `docs/VM_IMAGE.md`, which has the kernel options listed. |
| **Several v86 VMs in one page, cabled by the page** | **Works — adopted.** Each VM's `net0-send` goes into an isolating Ethernet switch (segments, MAC learning). Two VMs ping each other at ~1 ms. A Linux router VM on two segments forwards with TTL decrement, `ip_forward=0` really breaks it, and traceroute shows the hop. Cost is about 150 MB of browser memory and ~5 s (laptop) to 16 s (mid phone) to boot per extra VM, so labs stop at two VMs. |
| DHCP / DNS practice | **Works — adopted.** BusyBox has `udhcpc` but no DHCP server, so the page's services host runs a DHCP server (DISCOVER→OFFER→REQUEST→ACK, NAK, RELEASE, options 1/3/6/15/51/54) and a DNS server (A, PTR, NXDOMAIN). Real `udhcpc` writes the real `/etc/resolv.conf`; real `nslookup` and the libc resolver use them. BusyBox `dnsd` exists if a later lab wants students to run the DNS server themselves. |
| Single-NIC limit | v86 gives each VM one NIC. The router uses one interface holding a gateway address in each subnet, and the switch keeps the two LANs apart, so traffic really crosses the router. ICMP redirects are off on the router. True router-on-a-stick (802.1Q sub-interfaces) needs the institution image. |
| Cisco IOS | No emulator for IOS can be legally redistributed for a browser. The IOS labs stay simulated. The routing concepts have the real Linux twin. |

## Windows: what is and is not feasible

- **Windows cannot run in the browser.** v86 emulates a 32-bit x86 with no hardware virtualisation. Windows
  10/11 need x86-64, 4 GB+ of RAM, TPM 2.0 and Secure Boot. Old 32-bit Windows does run in v86, but slowly, it is
  not the curriculum, and licensing rules out serving it. There is no honest way to make "real Windows" a browser
  lab.
- **Kept: high-fidelity simulations.**
  - Windows CLI/PowerShell: the `ipconfig`, `netsh`, `Get-*` and printer cmdlets families, with aliases, errors
    and "did you mean".
  - The Windows 11 GUI: Settings, Services, Device Manager, ncpa.cpl and ADUC.
  - All are graded on the server and work on phones.
  - Where the skill is OS-neutral (DHCP, DNS, routing, permissions, services), a real Linux twin exists.
- **Later option: hosted Windows VMs.**
  - **The contract is ready.** Grading would use the same contract as the in-browser VMs. The LMS issues a
    nonce'd probe (here, a PowerShell script). The VM runs it through WinRM or the guest agent and posts
    `key value` lines back. The existing `vm_checks` / `grade()` code then decides the objectives. Only the probe
    language and transport change.
  - **Hosting options to evaluate:**
    - Proxmox or Hyper-V with Apache Guacamole, for HTML5 RDP in the LMS page (on-prem; cheapest at scale; needs
      ops staff)
    - Azure Virtual Desktop or Windows 365
    - AWS-hosted Windows desktops
  - **Azure Lab Services is not an option.** It is closed to new customers and retires on **28 June 2027**
    (Microsoft retirement guide).
  - **What hosting costs.** Per-student-hour compute and licensing, a reset-to-snapshot workflow, idle
    shutdown, and network isolation for each student. Check the current pricing before planning.
  - **When it is worth it.** For the Windows-only skills (Group Policy, AD on a real DC, BitLocker, Windows
    Recovery), a pilot with one class section would show whether the cost is justified over the simulators plus
    the classroom labs CL-6/CL-8/CL-13.

## How to verify

```
venv/bin/python tools/vm_headless.py linux-vm-routing            # boots the real VMs in Node and grades the solution (exit 0)
venv/bin/python tools/vm_headless.py linux-vm-routing --commands none   # nothing done → only "boot" (exit 0)
venv/bin/python tools/labs_e2e.py --only '^linux-vm-' --views desktop,phone,tablet
venv/bin/python tools/vm_device_check.py --cpu 4                 # throttled phone: boot, save → reload → resume, reset
```
