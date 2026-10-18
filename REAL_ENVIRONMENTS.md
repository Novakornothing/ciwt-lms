# Real environments vs simulated labs

Status 18 Oct 2026 (round 2), `labs` branch. Image, licences and measurements are in `docs/VM_IMAGE.md`.

## Summary

- **Real by default for Linux.**
  - **15 labs run on genuine Linux machines** that boot in the student's browser (v86 → WebAssembly). Five of
    them run two machines on a virtual network. Two more real-VM labs are stages inside lab scenarios (see
    below), so **17 graded pages are real**.
  - The image is our own build (`ciwt-linux.bin`, 10.8 MB, 13.3 MB total first download). It has real OpenSSH,
    sudo, shadow, iptables, dnsmasq, apk, e2fsprogs and util-linux, and a blank disk for the storage lab.
  - They are graded by reading the VM's real state:
    - files, modes and owners
    - users, groups, password ageing, locks, and sudoers as `sudo -l` sees it
    - running processes, listening sockets, init scripts and rc links
    - crontabs that **really fired**
    - syslog
    - partitions, filesystems, labels and UUIDs, fstab (`findmnt --verify`), swap
    - iptables rules and policies, plus saved rules
    - sshd's effective config (`sshd -T`), keys and permissions
    - addresses, routes, `ip_forward`, resolv.conf, hosts files, dnsmasq config
    - live `ping`, `ssh`, `curl`, `drill` and TCP connects run by the probe
  - Grading also uses the virtual network's own evidence (DHCP ACK, DNS query, forwarded query, a traceroute probe
    reaching the far router) and the ordered command history.
  - There is no server cost and no per-student VM to manage. Everything works offline once the files are cached.
- **The simulated version stays as a fallback.** Every real lab names one or more (`fallback`). For cron, ssh keys
  and scripting, the nearest simulator is the generic `linux-shell`, so on a weak device those three are better
  done on a lab computer. The page links to the fallback and recommends it automatically when the device is weak: under 2 GB of
  reported memory, no WebAssembly, or a boot over 45 s. Each simulator page in turn links to its real twin.
- **Networking is real between machines.** The VMs' kernels really do the ARP, routing, forwarding, TTL decrement,
  DHCP client and server, resolver, DNS server, firewall and traceroute. A small services host in the page answers
  as an upstream DHCP/DNS server, gateway, core router and remote host (`static/js/lab-vmnet.js`). The Packets tab
  shows every frame.
- **Windows and Cisco IOS stay high-fidelity simulations.** Round 2 raised the Windows output fidelity and added
  branching on wrong turns. See "Windows" below.
- **Lab scenarios (PBQ mode).** Two multi-stage tickets chain a Windows simulation stage with a real-VM stage, and
  hide the objectives until the end. See "Lab scenarios" below.

## Labs: real vs simulated

| # | Lab | Kind | Environment |
|---|---|---|---|
| 1 | `win-ipconfig` — 1. Windows 11 VM — Read Network Identity | windows | Simulated |
| 2 | `win-dns-break` — 2. Windows 11 VM — DNS Failure Isolation | windows | Simulated — real twin: `linux-vm-netclient`, `linux-vm-dns` |
| 3 | `win-dhcp-renew` — 3. Windows 11 VM — DHCP Release / Renew | windows | Simulated — real twin: `linux-vm-netclient`, `linux-vm-nettrouble` |
| 4 | `win-full-triage` — 4. Windows 11 VM — Full Client Triage | windows | Simulated |
| 5 | `w11-inventory` — 5. Windows 11 VM — Inventory the Endpoint | windows | Simulated |
| 6 | `w11-powershell-net` — 6. Windows 11 VM — PowerShell Network View | windows | Simulated |
| 7 | `w11-services` — 7. Windows 11 VM — Service Health | windows | Simulated — real twin: `linux-vm-packages` |
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
| 24 | `w11-firewall` — Windows 11 VM — Firewall profiles | windows | Simulated — real twin: `linux-vm-firewall` |
| 25 | `w11-disk` — Windows 11 VM — List disks | windows | Simulated — real twin: `linux-vm-disk` |
| 26 | `gui-devices` — Windows 11 GUI — Device Manager | win11gui | Simulated |
| 27 | `sw-port-security` — Switch — Port security on an access port | switch | Simulated |
| 28 | `rtr-default-route` — Router — Default route to the WAN | router | Simulated — real twin: `linux-vm-routing`, `linux-vm-nettrouble` |
| 29 | `sw-banner` — Switch — Login banner | switch | Simulated |
| 30 | `w11-wlan` — Windows 11 VM — WLAN report | windows | Simulated |
| 31 | `sw-mac-table` — Switch — MAC address table | switch | Simulated |
| 32 | `rtr-describe` — Router — Interface description | router | Simulated |
| 33 | `win-arp` — Windows 11 VM — ARP cache | windows | Simulated |
| 34 | `sw-int-status` — Switch — Interface status | switch | Simulated |
| 35 | `rtr-trace` — Router — Traceroute | router | Simulated — real twin: `linux-vm-nettrouble` |
| 36 | `win-route` — Windows 11 VM — Route table | windows | Simulated |
| 37 | `win-getmac` — Windows 11 VM — MAC address | windows | Simulated |
| 38 | `win-netstat` — Windows 11 VM — Active connections | windows | Simulated |
| 39 | `win-hostname` — Windows 11 VM — Hostname | windows | Simulated |
| 40 | `win-ping-loop` — Windows 11 VM — Loopback ping | windows | Simulated |
| 41 | `win-nslookup-ok` — Windows 11 VM — Working name lookup | windows | Simulated — real twin: `linux-vm-dns` |
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
| 52 | `linux-shell` — Linux shell — files, permissions and logs | linux | Simulated — real twin: `linux-vm-perms`, `linux-vm-shell`, `linux-vm-services`, `linux-vm-logs`, `linux-vm-cron`, `linux-vm-users`, `linux-vm-packages`, `linux-vm-ssh`, `linux-vm-script` |
| 53 | `print-trouble` — PowerShell — clear a stuck print queue | windows | Simulated |
| 54 | `rtr-vlan-acl` — Router — inter-VLAN routing and a guest ACL | router | Simulated — real twin: `linux-vm-firewall` |
| 55 | `sw-vlan-multi` — Switch — two VLANs, access ports and a pruned trunk | switch | Simulated |
| 56 | `wifi-secure` — SOHO router — secure the admin page, Wi-Fi and guest network | activity | Simulated |
| 57 | `sec-malware` — Malware response — the seven-step removal process | activity | Simulated |
| 58 | `ops-backup` — Backup and recovery — types, restore sets, 3-2-1, RPO/RTO | activity | Simulated |
| 59 | `virt-vm` — Virtualization — build a Windows 11 lab VM | activity | Simulated |
| 60 | `mob-mdm` — Mobile devices — connectivity and MDM tickets inside policy | activity | Simulated |
| 61 | `win-ad-users` — Active Directory Users and Computers — onboard, unlock, offboard | win11gui | Simulated — real twin: `linux-vm-users` |
| 62 | `win-laptop-ports` — Windows CLI — battery health, VM check, MX records and port tests | windows | Simulated |
| 63 | `win-wifi-survey` — Windows CLI — Wi-Fi survey on a laptop (signal, band, channel) | windows | Simulated |
| 64 | `hv-vswitch` — Hyper-V host — isolated virtual switch and checkpoints (PowerShell) | windows | Simulated |
| 65 | `linux-vm-perms` — Real Linux VM — files, ownership, permissions and a support script | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 66 | `linux-vm-shell` — Real Linux VM — shell basics: files, permissions, scripts and logs | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 67 | `linux-vm-services` — Real Linux VM — services, processes, a filling disk, cron and syslog | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 68 | `linux-vm-netclient` — Real Linux VM — lease, gateway and name resolution on a live network | vm | **Real** — 1 Linux VM in the browser + virtual network (DHCP/DNS host); fallback: `win-dhcp-renew`, `win-dns-break` |
| 69 | `linux-vm-routing` — Real Linux VMs — route between two networks (two machines, one router) | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `rtr-two-interfaces`, `rtr-default-route` |
| 70 | `linux-vm-logs` — Real Linux VM — log investigation: brute force, a breach and a failed backup | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 71 | `linux-vm-cron` — Real Linux VM — scheduled tasks that never ran (cron) | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 72 | `linux-vm-users` — Real Linux VM — accounts, groups and least-privilege sudo for a help-desk team | vm | **Real** — 1 Linux VM in the browser; fallback: `win-ad-users`, `linux-shell` |
| 73 | `linux-vm-packages` — Real Linux VM — package and service troubleshooting (apk, init scripts, ports) | vm | **Real** — 1 Linux VM in the browser; fallback: `w11-services`, `linux-shell` |
| 74 | `linux-vm-firewall` — Real Linux VMs — host firewall with iptables (default deny, stateful, admin-only SSH) | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `w11-firewall`, `rtr-vlan-acl` |
| 75 | `linux-vm-disk` — Real Linux VM — add a data disk: partitions, ext4, mount by UUID, swap and fstab | vm | **Real** — 1 Linux VM in the browser; fallback: `w11-disk` |
| 76 | `linux-vm-ssh` — Real Linux VMs — SSH between two machines with keys, then turn passwords off | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `linux-shell` |
| 77 | `linux-vm-script` — Real Linux VM — automate it: a backup script with rotation, exit codes and logging | vm | **Real** — 1 Linux VM in the browser; fallback: `linux-shell` |
| 78 | `linux-vm-dns` — Real Linux VMs — DNS troubleshooting chain: client, internal resolver, records and forwarding | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `win-dns-break`, `win-nslookup-ok` |
| 79 | `linux-vm-nettrouble` — Real Linux VMs — multi-VM network troubleshooting: no lease, wrong gateway, broken route | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `win-dhcp-renew`, `rtr-default-route`, `rtr-trace` |
| 80 | `scn-dns-evidence` — SCN-DNS · Stage 1 · User's PC (Windows 11 simulation) | windows | Simulated |
| 81 | `scn-dns-fix` — SCN-DNS · Stage 2 · DNS server and test client (2 real Linux VMs) | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `win-dns-break`, `win-nslookup-ok` |
| 82 | `scn-lan2-fix` — SCN-LAN2 · Stage 1 · LAN 2 router and PC (2 real Linux VMs) | vm | **Real** — 2 Linux VMs in the browser + virtual network; fallback: `win-dhcp-renew`, `rtr-default-route`, `rtr-trace` |
| 83 | `scn-lan2-verify` — SCN-LAN2 · Stage 2 · CFO's laptop (Windows 11 simulation) | windows | Simulated |
| – | `CL-4` — Print path and laptop FRU identification | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-6` — Build, snapshot and network a virtual machine | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-7` — Structured troubleshooting drills on staged faults | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-8` — Windows recovery ladder in a lab VM | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-9` — Linux command line and permissions | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-10` — Endpoint security posture check and incident tabletop | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-11` — Slow PC: resource tools and clean-boot isolation | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-12` — Change request and recovery drill | classroom | **In class** — real equipment or lab VMs, instructor sign-off |
| – | `CL-13` — PowerShell evidence and name-resolution repair | classroom | **In class** — real equipment or lab VMs, instructor sign-off |

**Real environment: 15 labs, plus 2 real-VM scenario stages.**
- Round 1: `linux-vm-perms`, `linux-vm-shell`, `linux-vm-services`, `linux-vm-netclient`, `linux-vm-routing`
- Round 2: `linux-vm-logs`, `linux-vm-cron`, `linux-vm-users`, `linux-vm-packages`, `linux-vm-firewall`,
  `linux-vm-disk`, `linux-vm-ssh`, `linux-vm-script`, `linux-vm-dns`, `linux-vm-nettrouble`
- Scenario stages: `scn-dns-fix`, `scn-lan2-fix`

**Simulated: 64 labs, plus 2 Windows scenario stages.** Of the 64, 12 now have a real twin. **9 classroom labs**
(CL-*) use real equipment with an instructor's sign-off.

## What each real lab checks inside the machine

| Lab | Machine state read by the probe | Network / history evidence |
|---|---|---|
| linux-vm-perms | directory exists, file content, mode `-rw-r-----`, user `tech1` exists and owns the file, `check.sh` is executable and prints `disk ok` when run | `ls -l` after `chmod` |
| linux-vm-shell | `logs/` and `notes.txt` exist, `backup.sh` has the owner x bit **and really ran** (its marker in `/tmp/backup`), report.txt others-r removed | `whoami`/`hostname`, `cd` then `ls -l`, `grep ERROR app.log` |
| linux-vm-services | runaway `debugdump` is no longer in `ps`; `/tmp` space freed; the init script is executable with the correct `DAEMON=`; `S50heartbeat status` says running and the log grows; root's crontab has `*/15 … cleanup.sh`; `SR-4201` is in `/var/log/messages` | investigated (`df`/`du`, then `ps`/`fuser`) before acting; status checked after start |
| linux-vm-netclient | eth0 holds a 10.10.0.100–150 lease; default route via 10.10.0.1; `nameserver 10.10.0.53`; the stale `/etc/hosts` line is gone; `ping intranet.ciwt.lab` really reaches 10.10.0.80 | the DHCP server sent an ACK (a hand-typed address does not count); the gateway saw a ping; the DNS server saw the query; `ip a` before `udhcpc`; `ip neigh` |
| linux-vm-routing | pc-a 10.1.0.10/24 and default via 10.1.0.1; rtr-1 has 10.1.0.1/24 + 10.2.0.1/24 and `ip_forward=1`; pc-a's live ping to 10.2.0.10 returns with **TTL 63**, so it was really routed | the fault was isolated (ping from the PC, then from the router) *before* forwarding was enabled; traceroute run on pc-a |
| linux-vm-logs | the evidence copy matches the original by sha256 and the originals are untouched; the answers file names the attacker IP, failure count, breached account, OOM-killed process and the backup target from the *rotated, gzipped* log (compared by hash, so the answers are not in the probe); `SR-5120` is in syslog via `logger` | the backup answer counts only if the rotated `.gz` log was really read |
| linux-vm-cron | `crond` running and enabled (`S50crond`); root's crontab has `30 2 * * 1-5 /usr/local/bin/backup.sh`; `rotate-logs` executable; user `reports` has a weekday 07:30 job (`crontab -u`); the every-minute heartbeat **wrote its file after the student's edit** | inspected (`crontab -l`, `service crond status`) before changing anything |
| linux-vm-users | group `helpdesk`; users `ana`/`ben` in it with a password set and `chage -d 0` (must change); `/srv/helpdesk` is group-owned with mode 2770; `/etc/sudoers.d/40-helpdesk` is mode 440 and gives `ana` exactly the `service` and `tail` commands (read from `sudo -l -U ana`); `jdoe` is locked; `90-temp` is removed | verified as an auditor would, with `sudo -l -U ana` |
| linux-vm-packages | the dead repository line is commented out; `darkhttpd` is installed per the apk database; the `socat` process squatting on :8080 is gone; the `webd` init script runs and `S50webd` exists; `curl localhost:8080` returns the page | diagnosed first (`service webd start` to read its error, then `apk search`) |
| linux-vm-firewall | `iptables -S` has lo and ESTABLISHED,RELATED accepts, 80/tcp and ICMP, 22/tcp only from 10.20.0.50, and INPUT policy DROP; the final rules are saved to `/etc/iptables/rules-save`; **from the second VM (adm-ws)**, the probe's TCP connects to 22 and 80 succeed and the blocked ports fail | a baseline (`portcheck 2323` from adm-ws, `ss -tlnp`/`iptables -S` on web-01) before the policy change |
| linux-vm-disk | `/dev/sda1` (32 MB, Linux) and `/dev/sda2` (type 82, swap) exist; sda1 is ext4 with label `appdata`; `/srv/data` is mounted from it and holds the migrated files; fstab mounts it by UUID; swap is on and in fstab; the stale `olddata` line is gone; `findmnt --verify` is clean | the new disk identified (`lsblk`) before partitioning |
| linux-vm-ssh | on app-01, the `PermitRootLogin noo` typo is fixed and `sshd -T` shows `passwordauthentication no` and `permitrootlogin no`; on dev-ws, an ed25519 key exists with correct `~/.ssh` permissions and app-01's host key is in known_hosts; **the probe really logs in with the key in BatchMode, and a password-only login is refused**; `release-1.4.txt` arrived by scp with a matching sha256 | the refusal check proves sshd was really restarted |
| linux-vm-script | black-box tests of the student's `app-backup.sh`: no argument exits 2 with usage; a missing source exits 1; a run makes `app-YYYYMMDD-HHMM.tar.gz` holding the right files; rotation keeps the newest 3 (fixture with back-dated archives); it logs `backup ok` to syslog; cron has `15 1 * * *` and the script has really run | behaviour only: the probe never reads the script's text, apart from rejecting the starter's "not implemented yet" |
| linux-vm-dns | ws-22's resolv.conf points at dns-01; dnsmasq listens on 10.30.0.53; `intranet.ciwt.lab` resolves to 10.30.0.80 from `/etc/hosts.ciwt`; MX and a CNAME `wiki` exist; forwarding is to 10.30.0.1, and **the upstream resolver saw a forwarded query** (`dns_fwd` fabric); the probe's `drill` from ws-22 gets the right answers | diagnosed from the client first (`cat /etc/resolv.conf`, `drill`); verified with both `drill` and `nslookup` |
| linux-vm-nettrouble | rtr-2's dnsmasq is running with a valid DHCP range (the `dhcp-rnage` typo is fixed) and hands out router 10.2.0.1; rtr-2's default route goes via 10.1.0.1 with forwarding on; pc-7 holds a real lease from rtr-2; its live ping to 198.51.100.10 shows **TTL 62** (two real hops) | the symptom was recorded (`udhcpc`, `dnsmasq --test`); the fault was isolated (ping from pc-7, `ip route` on rtr-2) before the route was changed; the core router saw a traceroute probe from pc-7 (`trace_core`) |

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
| Network namespaces / veth / bridge inside one VM | **The round-2 image kernel has veth, bridge, dummy and 802.1Q** (`docs/VM_IMAGE.md`), but the labs still build networks between VMs. That is what the students see in the field, and the Packets tab shows it. The upstream image could do none of this. |
| **Several v86 VMs in one page, cabled by the page** | **Works — adopted.** Each VM's `net0-send` goes into an isolating Ethernet switch (segments, MAC learning). Two VMs ping each other at ~1 ms. A Linux router VM on two segments forwards with TTL decrement, `ip_forward=0` really breaks it, and traceroute shows the hop. Cost is about 150 MB of browser memory and ~5 s (laptop) to 16 s (mid phone) to boot per extra VM, so labs stop at two VMs. With the new image it is about 80 MB of guest RAM per VM. |
| DHCP / DNS practice | **Works — adopted.** BusyBox has `udhcpc` but no DHCP server, so the page's services host runs a DHCP server (DISCOVER→OFFER→REQUEST→ACK, NAK, RELEASE, options 1/3/6/15/51/54) and a DNS server (A, PTR, NXDOMAIN). Real `udhcpc` writes the real `/etc/resolv.conf`; real `nslookup` and the libc resolver use them. In round 2, students run **real dnsmasq** as the DNS server (linux-vm-dns) and as the DHCP server on a router (linux-vm-nettrouble). The services host is then only the upstream resolver and core router. |
| Firewalls | **Real iptables** (nf_tables backend) on the VM kernel; the second VM proves the rules from outside. |
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
- **Round 2: Windows fidelity (`win_fidelity.py`).** A rendering layer runs after the simulator's engine.
  Grading reads the same state, so grading did not change (`tests/test_win_fidelity.py` re-runs every
  solution).
  - `ipconfig` and `ipconfig /all` print every Windows 11 field (DHCP lease times, IAID/DUID, NetBIOS over Tcpip),
    the post-`/release` form and APIPA 169.254.x.x.
  - `ping` prints Windows' statistics block, honours `-n`, and gives "Destination host unreachable" from the
    PC's own address or "General failure", whichever matches the fault.
  - `tracert` agrees with `ping` about what is reachable. Where the model ends, it says "simulator stops here"
    rather than inventing hops.
  - Also re-rendered: `nslookup` (default server, `nslookup name server`, timeouts against a wrong server,
    Non-authoritative answer), `Resolve-DnsName`, `Test-NetConnection`, `Get-Service`, `getmac`, `arp -a` and
    `route print`.
  - **Wrong turns branch.**
    - Changing DNS or IP settings without elevation gets Windows' real "requires elevation" / "Access is denied"
      text.
    - Releasing twice gives the real "no adapter is in the state permissible" error.
    - Flushing DNS before diagnosing, releasing when DHCP was not the fault, or "fixing" with a flush leads to a
      state-specific note. It is recorded as a wrong turn, and the instructor and the scenario debrief see it.
  - **Honesty is kept.** Every simulator still says it is a simulation, and so do the elevation and
    "stops here" notes.
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

## Lab scenarios (PBQ mode)

`/labs/scenario/<id>` (`labs_scenario.py`). Each scenario is a ticket that gives only the user's complaint. Its
stages are separate graded labs and unlock in order.

| Scenario | Stage 1 | Stage 2 |
|---|---|---|
| SCN-DNS: "intranet and the internet are both down for one user" | `scn-dns-evidence`: user's PC (Windows 11 simulation). Gather evidence, isolate DNS. | `scn-dns-fix`: DNS server + client (2 real Linux VMs). Fix the resolver, zone and forwarder. |
| SCN-LAN2: "the CFO on LAN 2 has no network" | `scn-lan2-fix`: router + PC (2 real Linux VMs). DHCP typo, wrong router option, broken default route. | `scn-lan2-verify`: CFO's laptop (Windows 11 simulation). Renew and prove the path. |

- **No objectives up front.** The checks panel shows "Hidden check 1…n". A check that passes shows ✓ without
  its text, and the full list appears only when the stage is done.
- **Hints and the event log still work.** The event log keeps the real check text and reasons for the
  instructor. Check responses to the student are worded like a PBQ ("a hidden check is not met yet").
- **The hub shows each stage's state:** score, hints used, failed checks, wrong turns, minutes, and
  locked/unlocked.
- **Fallbacks.** The VM stages keep their sim fallbacks. A fallback is practice only: it does not complete the
  stage.

## How to verify

```
venv/bin/python tools/vm_headless.py linux-vm-routing            # boots the real VMs in Node and grades the solution (exit 0)
venv/bin/python tools/vm_headless.py linux-vm-routing --commands none   # nothing done → only "boot" (exit 0)
venv/bin/python tools/labs_e2e.py --only '^linux-vm-' --views desktop,phone,tablet
venv/bin/python tools/labs_e2e.py --only '^scn-' --views desktop,phone,tablet           # scenario stages
venv/bin/python -m pytest tests/test_win_fidelity.py tests/test_scenario.py -q
venv/bin/python tools/vm_device_check.py --cpu 4                 # throttled phone: boot, save → reload → resume, reset
```
