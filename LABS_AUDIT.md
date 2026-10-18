# Live labs audit (labs branch)

Audit date 17 Oct 2026. Every live lab was run as a student against a copy of the database (`labs_dev.db`, server on
port 5191; the real `ciwt_lms.db` was not touched). The checks were: start → steps → auto-grade → progress and
gradebook → instructor view, at 390 px (phone, touch), 820 px (tablet, touch) and 1440 px (desktop).
The **baseline** was the code at the branch point. It was probed with a Playwright script that drove each lab
through its UI and then reloaded. **Now** is the code at the end of this branch, checked by
`tools/labs_e2e.py`, which completes every lab through the real UI at all three widths and then checks:

- the DB records
- reload-resume
- overflow
- the instructor pages

## Headlines

**Baseline: 46 labs.**
- **7 of 46 could not be finished on a phone.** These were the Windows 11 GUI labs: their side navigation
  and targets were off-screen or covered at 390 px.
- **No lab survived a reload.** State lived in the Flask session cookie, which has a 4 KB limit and is lost on
  re-login. The probe saw 0 ticked objectives after every reload.
- **Completion could be faked.** `mark-done` trusted a `done` list sent by the client.
- **Instructors could not see lab work.** Labs had no gradebook column and no per-student lab view.
  Classroom labs (CL-*) could not be recorded at all.
- **The /labs index was incomplete.** It omitted the ticket and hardware labs.
- **The client-side fallback engine never recorded completion.**

**Grading and simulator bugs:**
- **Ticket intake** accepted any answer.
- **DHCP renew** did not enforce the release → renew → test order.
- **The gateway stayed pingable** after `ipconfig /release`.
- **The router** replied to pings through interfaces that were shut down.
- **The `rtr-default-route` hint sequence failed.** IOS has no parent-mode fallback, so `ip route` typed in
  config-if was rejected.
- **`sh int status` was rejected as ambiguous.**
- **Names and descriptions containing spaces broke.**
- **The `gui-renew` instructions** told students to use a Renew button that Windows 11 does not have.
- **There were no "did you mean" suggestions** and no Linux equivalents for Windows habits.

**Now: 69 labs (46 original + 23 new, including five real Linux VM labs) plus 9 classroom labs (CL-4, CL-6…CL-13).**
- All 69 labs complete through the UI at desktop, phone and tablet.
- Each completion checks:
  - a server-side record (`lab_progress` score 100 plus a `lab_completion` row)
  - reload resume (every objective still ticked)
  - no horizontal overflow
  - the instructor views
- CL-4…CL-13 are signed off in the UI by the instructor, and the student sees the score and the feedback.
- Results per lab and view are in the table below.

## What was broken → what is fixed

| Area | Baseline | Now |
|---|---|---|
| Persistence | Session cookie. Lost on reload or re-login. | `lab_progress` table per user and lab: state, transcript (last 400 lines), undo stack, hints, attempts, time, best score. Every page resumes where the student left off. |
| Integrity | `mark-done` trusted the client. | Objectives are decided only on the server from the server-side state. `mark-done` re-checks that state (test `test_mark_done_cannot_be_faked`). |
| Reset / undo | Reset reloaded the page only. No undo. | **Start over** gives a new seeded attempt and keeps the best score. **Undo** reverts the last configuration change (objectives already earned stay earned). |
| Hints | A static list. | Two tiers per objective (a nudge, then the exact action). Hints are counted and shown to the instructor. |
| Gradebook | No labs. | A "Live labs" category (weight 0 by default, set per section) and one Labs column that links to the per-lab results. It also appears in the syllabus grading table. |
| Instructor | Nothing. | **Lab results** per section: by lab, by student, CSV. Per-student detail: transcript, process summary, event log. Classroom-lab sign-off with a 4-criterion rubric and feedback. |
| Process data | None. | An ordered event log per attempt (`lab_event`): every command, GUI action, answer check, hint, undo, reset, completion and VM line, with outcome and newly earned objectives. Instructors get a per-attempt summary (actions, unrecognised commands, wrong answers, repeats, hints, minutes) and a CSV export. Passwords typed in AD dialogs are masked. |
| ticket-intake | Any answer ticked the objective. | Checks classify = incident, impact = many, escalate = yes, with feedback on each wrong value. |
| win-dhcp-renew | Steps could be done in any order. The gateway answered while released. | The gateway test must come after release and renew. Pings fail while released, with a message telling the student to renew first. |
| IOS | No parent-mode fallback. `sh int status` was ambiguous. Spaces broke names and descriptions. Shut interfaces still pinged. | Global commands work from sub-modes as on real IOS. Abbreviations are disambiguated. Quoted and spaced names work. Down interfaces drop pings. Added sub-interfaces (`encapsulation dot1Q`), ACLs (standard and extended, `ip access-group`), trunk allowed lists, `show access-lists`, and ACL order and placement tips. |
| Windows sim | Few aliases. | PowerShell aliases (gip, gsv, gps, tnc, gc…). `/?` usage. "Did you mean". Printers and the spooler (both the PowerShell and the `net stop` / `del spool\PRINTERS` paths). A DNS-primary-down scenario. `systeminfo` reports *System Model: Virtual Machine* and the hypervisor line. |
| Linux | No Linux lab. | A bash-style shell with files, permissions, `chmod` (octal and symbolic), scripts, `grep`, Tab completion, case-sensitivity "did you mean", and Windows-habit hints (`dir` → `ls`). |
| gui-renew | Pointed to a Renew button Windows 11 does not have. | Instructions, hints and the lab manual all say: Advanced network settings (or ncpa.cpl) → Disable → Enable. |
| Mobile GUI | Not completable at 390 px. | Rebuilt as a server-driven desktop (see Mobile). |
| Index | Ticket and hardware labs missing. | Grouped by kind with progress badges (Resume / Open / Launch). Classroom labs are listed too. |

## Mobile

### Terminal (all CLI kinds and the VM)

- **Inputs are 16 px**, so iOS does not zoom on focus.
- **Keys bar:** Tab, ↑, ↓, Ctrl-C, Clear, help (the VM bar adds Ctrl-D, Esc and Check ✓). Pressing these keys
  does not close the on-screen keyboard (`pointerdown` with preventDefault).
- **Command chips** insert text without running it.
- **Focus mode** turns on automatically at < 700 px. It is a fixed overlay sized from `visualViewport`, so it
  survives the on-screen keyboard and rotation.
- **Checkpoints:** when the last command objective is done and a checkpoint question remains, the terminal leaves
  focus mode and scrolls to the question. This came out of the phone e2e: the question was hidden behind the
  overlay.
- **Long output wraps** (`overflow-wrap:anywhere`, pre-wrap).
- **Failed sends** show a Retry button. Commands typed while a request is in flight are queued.

### Windows 11 GUI

- **Narrow mode** (container < 640 px):
  - the desktop icons become a row
  - the window is full-width
  - Settings uses a list → pane → Back pattern
  - the split views stack
- **Height** comes from `visualViewport`, so the desk works in portrait and landscape.
- **Touch targets** are at least 44 px.
- **Long-press (550 ms) = right-click** on the adapter tile, services and AD users. Right-click and the
  ContextMenu key (or Shift+F10) also work.
- **Start search** accepts settings, services.msc, devmgmt.msc, ncpa.cpl and dsa.msc.
- **Dialogs keep typed values and focus across re-renders.** This fixes a focus race that the e2e caught on the
  AD lab.

### Activities

- **Match:** tap an item, then tap the target box. Mouse drag and touch drag (pointer events) also work, and
  every step has a keyboard path.
- **Order:** ↑/↓ buttons plus drag on the handle.
- **Config pages** use real switches and selects. Build steps show a running total.

## New labs (20)

Each has the following, and the first 15 have been in place since the start of the branch:
- the standard lab format (objective, steps, expected results, equipment, low-cost option, troubleshooting,
  reflection, rubric)
- course-objective mapping
- server-side auto-grading
- hints for every objective
- mobile support
- e2e coverage at three widths

They appear in CHAPTER_LABS, so they flow into the lab manual, lesson plans and pacing tables (`augment_pacing`).

| Lab | Course | What the student does |
|---|---|---|
| net-subnet | NETOPS 1, ITSUP 5 | Per-student generated subnets: network, broadcast, range, usable hosts, prefix sizing, APIPA |
| hw-cables | NETOPS 2, ITSUP 3 | Match SVG connectors, match cable to job, pick the right tool |
| hw-pc-build | ITSUP 2–3 | Build to a budget and requirements (validator); UEFI / Secure Boot choice |
| ticket-method | NETOPS 6, ITSUP 7 | Order the troubleshooting method, triage choices, write a ticket note (checked) |
| win-net-cli | ITSUP 13/5, NETOPS 4 | Prove the primary DNS server is down with evidence (ipconfig, ping by IP, nslookup to each server) |
| linux-shell | ITSUP 9 | Simulated bash: navigate, mkdir, echo >, chmod, run a script, grep a log |
| print-trouble | ITSUP 4/13 | Stuck queue: Get-Printer, Test-Connection, remove only the job in Error, restart the spooler, test page (the cmd spool-folder path is also modelled, with its cost) |
| rtr-vlan-acl | NETOPS 2/4/5/9 | Router-on-a-stick sub-interfaces, trunk, extended ACL, apply and verify |
| sw-vlan-multi | NETOPS 2/9 | Several VLANs, access ports, trunk with an allowed list |
| wifi-secure | NETOPS 3/5, ITSUP 5 | SOHO router pages: SSID, WPA3, passphrase, WPS off, channel |
| sec-malware | ITSUP 10 | Malware removal steps in order, with decisions |
| ops-backup | ITSUP 12 | 3-2-1 backup plan, restore test, RPO/RTO |
| virt-vm | ITSUP 6 | Hypervisor types, VM sizing, snapshots |
| mob-mdm | ITSUP 4 | MDM enrolment and policy decisions without bypassing policy |
| win-ad-users | ITSUP 8/10 | ADUC desktop: create a user in the right OU (password policy), least-privilege group, unlock and reset, disable a leaver (delete refused) |
| **win-laptop-ports** | ITSUP 4/5/6 | Battery report (canned; the VM has no battery, as on a real VM), "Virtual machine" check in systeminfo, MX records, Test-NetConnection on ports 25 and 587 |
| **win-wifi-survey** | ITSUP 5, NETOPS 3 | A simulated laptop **with** a Wi-Fi adapter: show interfaces, show networks mode=bssid, profiles, reconnect to 5 GHz, verify |
| **hv-vswitch** | ITSUP 6 | A simulated Hyper-V host: Get-VM, Get-VMSwitch, New-VMSwitch Private (with feedback if Internal or External is chosen), Connect-VMNetworkAdapter, Checkpoint-VM, Get-VMCheckpoint, Restore-VMCheckpoint |
| **linux-vm-perms** | ITSUP 9 | **Real Linux VM**: files, ownership, permissions and a support script |
| **linux-vm-shell** | ITSUP 9 | **Real Linux VM** twin of linux-shell (the simulator stays as the fallback) |
| **linux-vm-services** | ITSUP 9, NETOPS 5 | **Real Linux VM**: runaway process filling /tmp, broken init script, cron, syslog |
| **linux-vm-netclient** | ITSUP 5/13, NETOPS 4 | **Real Linux VM on a virtual LAN**: APIPA address → DHCP lease, gateway, DNS, stale hosts entry |
| **linux-vm-routing** | ITSUP 5, NETOPS 9 | **Two real Linux VMs**: address a PC and a Linux router, forwarding, default route, traceroute |
| (CL-4…CL-13) | — | Already existed as paper labs; they are now recorded through instructor sign-off |

### Pass-10 lab gaps from refinement (CURRICULUM_AUDIT "Pass 10")

| Gap | Filled by |
|---|---|
| 4.1 battery report | win-laptop-ports (canned report, plus the real `powercfg` error on a VM) |
| 4.3 hands-on spooler | print-trouble (PowerShell path, plus the `net stop` / `del spool\PRINTERS` / `net start` path) |
| 5.1–5.2 subnet drill and port/DNS-record lab | net-subnet; win-laptop-ports (`nslookup -type=MX`, `Resolve-DnsName -Type MX`, `Test-NetConnection -Port`) |
| 5.4 no wireless adapter on a VM | win-wifi-survey (simulated laptop adapter; works on phones) |
| 6.1 "Virtual machine" | `systeminfo` in every Windows lab (w11-inventory included) now shows *System Model: Virtual Machine* and the hypervisor line; win-laptop-ports grades it |
| 6.3 virtual switch and checkpoints | hv-vswitch (simulated Hyper-V host) |

## Real environments: real Linux is now the standard for the Linux and network-client skills

Full detail is in `REAL_ENVIRONMENTS.md`: a real-vs-simulated table for every lab, what each probe reads, the
networking evaluation and the Windows feasibility notes. The image, the measurements and an institution build
recipe are in `docs/VM_IMAGE.md`.

**Five labs run on real Linux machines that boot in the browser** (v86, kernel 6.8.12 and BusyBox 1.36.1).
Nothing runs on the server.

| Lab | Machines | Real state that is graded |
|---|---|---|
| linux-vm-perms | 1 | directory, file contents, mode 640, owner tech1, the script runs |
| linux-vm-shell | 1 | the linux-shell ticket on a real box: files, chmod, `backup.sh` really ran, `grep` |
| linux-vm-services | 1 | runaway process killed, `/tmp` freed, init script repaired and running, crontab entry, syslog line |
| linux-vm-netclient | 1 + virtual LAN | real `udhcpc` lease from the in-page DHCP server (ACK required), gateway, `resolv.conf`, stale `/etc/hosts` removed, live ping by name |
| linux-vm-routing | 2 + two LANs | addresses on the PC and the router, default route, `ip_forward`, live ping through the router with TTL 63, traceroute; the fault was isolated *before* forwarding was turned on |

**How grading works.**
- A generic engine (`labs_vm.py`) generates a probe for each machine from the lab's `vm_checks`. Each probe is
  run under a watchdog and carries a nonce and the machine name.
- Grading combines three kinds of evidence:
  - shell tests run inside the VM
  - the ordered command history (`hist` / `seq` / `before` rules)
  - evidence from the virtual network: the DHCP ACK, a ping to the gateway, the DNS query
- Each machine gets a hidden scenario setup on its first boot: broken services, a runaway process, an APIPA
  address, a stale hosts entry.

**Devices.**
- Machine tabs and a Packets tab (every frame summarised).
- The keys bar and focus mode work on phones.
- **Save** stores all the VMs plus the DHCP leases in IndexedDB.
- **Resume** takes about 1 s.
- **Reset** returns to the start of the scenario in under 1 s from an in-memory clean snapshot. Small phones in
  the two-VM lab cold-boot instead.
- Boot on a mid-range phone (CPU ×4) is about 9 s for one VM and 16 s for two. On an older phone (×6) it is
  about 15 s for one VM and 25 s for two.

**Fallback.**
- Every real lab names a simulated fallback, and its page links to it.
- The page recommends the fallback on weak devices (under 2 GB of reported memory, no WebAssembly, or a boot
  over 45 s).
- Each simulator links back to its real twin.

**Networking.**
- Namespaces, veth, bridges and VLANs are not in this kernel (tested). Several VMs cabled by an isolating switch
  in the page do give real routing.
- An in-page DHCP and DNS server gives real lease and resolution practice.

**Windows.** It cannot run in the browser, so the Windows labs stay high-fidelity simulators. A hosted-VM option
that reuses the same probe contract is described in `REAL_ENVIRONMENTS.md`.

**Verification:**
- `tools/vm_headless.py` boots each lab's real VMs in Node and runs the real grader. Every solution completes,
  and doing nothing earns only `boot`.
- `tools/labs_e2e.py` passes all five labs at desktop, phone and tablet.
- `tools/vm_device_check.py` runs on a throttled phone and checks:
  - boot
  - save → reload → resume (the VM's files persist)
  - cold and snapshot reset (the scenario is clean again)
  - axe on the booted console: 0 violations

**Trust.** The VMs run on the student's device, so a determined student could forge results. Treat these labs as
formative, or pair them with the event log (every line, per machine) or a sign-off.

## Per-lab inventory and results

Baseline D/P/T are the pre-change UI probe results (desktop 1440 / phone 390 / tablet 820). "Now" is
`tools/labs_e2e.py` (✅ = completed through the UI, then DB, resume, overflow and instructor checks).
Kind legend:

| Kind | What it is |
|---|---|
| windows | cmd / PowerShell simulator |
| win11gui | desktop simulator |
| switch / router | IOS simulators |
| linux | bash simulator |
| ticket | scenario desk |
| activity | drag, tap and type steps |
| vm | real Linux VM(s) in the browser (v86) |


## Inventory and results (e2e run of 18 Oct 2026, 246/246 checks passed: 234 lab×view + 12 instructor/classroom)

| # | Lab | Kind | Obj. | Course objectives | Chapters | Baseline D/P/T | Now D/P/T (e2e) |
|---|---|---|---|---|---|---|---|
| 1 | `win-ipconfig` — 1. Windows 11 VM — Read Network Identity | windows | 2 | – | CL6, IT13, IT5, NO1 | ok/ok/ok | ✅✅✅ |
| 2 | `win-dns-break` — 2. Windows 11 VM — DNS Failure Isolation | windows | 5 | – | CL6, IT13, IT5, IT7, NO4 | ok/ok/ok | ✅✅✅ |
| 3 | `win-dhcp-renew` — 3. Windows 11 VM — DHCP Release / Renew | windows | 4 | – | CL1, CL6, IT13, IT8, NO4 | ok/ok/ok | ✅✅✅ |
| 4 | `win-full-triage` — 4. Windows 11 VM — Full Client Triage | windows | 9 | – | CL6, IT13, IT7, NO6 | ok/ok/ok | ✅✅✅ |
| 5 | `w11-inventory` — 5. Windows 11 VM — Inventory the Endpoint | windows | 4 | – | CL1, CL6, IT13, IT5, IT8 | ok/ok/ok | ✅✅✅ |
| 6 | `w11-powershell-net` — 6. Windows 11 VM — PowerShell Network View | windows | 4 | – | CL1, CL6, IT13, IT8 | ok/ok/ok | ✅✅✅ |
| 7 | `w11-services` — 7. Windows 11 VM — Service Health | windows | 3 | – | CL1, IT11, IT8 | ok/ok/ok | ✅✅✅ |
| 8 | `w11-netsh` — 7b. Windows 11 VM — netsh interface view | windows | 2 | – | CL6, IT13, IT5 | ok/ok/ok | ✅✅✅ |
| 9 | `w11-processes` — 7c. Windows 11 VM — What's running | windows | 2 | – | CL6, IT11, IT13 | ok/ok/ok | ✅✅✅ |
| 10 | `gui-about` — 8. Windows 11 GUI — Settings About | win11gui | 3 | – | CL1, CL6, IT13, IT8 | ok/**fail**/ok | ✅✅✅ |
| 11 | `gui-ethernet` — 9. Windows 11 GUI — Ethernet properties | win11gui | 3 | – | CL6, IT13, IT5 | ok/**fail**/ok | ✅✅✅ |
| 12 | `gui-renew` — 10. Windows 11 GUI — Renew the Ethernet lease | win11gui | 4 | – | CL6, IT13 | ok/**fail**/ok | ✅✅✅ |
| 13 | `gui-services` — 11. Windows 11 GUI — Services | win11gui | 4 | – | CL1, CL3, IT10, IT8 | ok/**fail**/ok | ✅✅✅ |
| 14 | `gui-update` — 12. Windows 11 GUI — Windows Update | win11gui | 3 | – | CL1, CL6, IT13, IT8 | ok/**fail**/ok | ✅✅✅ |
| 15 | `gui-accounts` — 13. Windows 11 GUI — Accounts | win11gui | 2 | – | CL1, CL3, CL6, IT10, IT13, IT8 | ok/**fail**/ok | ✅✅✅ |
| 16 | `sw-vlan-access` — 5. Switch — VLAN + Access Port | switch | 4 | – | NO2, NO9 | ok/ok/ok | ✅✅✅ |
| 17 | `sw-trunk-basics` — 6. Switch — Trunk Uplink | switch | 3 | – | NO2, NO9 | ok/ok/ok | ✅✅✅ |
| 18 | `sw-vlan-and-trunk` — 7. Switch — VLAN + Access + Trunk (capstone) | switch | 6 | – | NO2, NO6, NO9 | ok/ok/ok | ✅✅✅ |
| 19 | `rtr-gateway` — 8. Router — Gateway Address + Ping | router | 4 | – | NO3, NO9 | ok/ok/ok | ✅✅✅ |
| 20 | `rtr-two-interfaces` — 9. Router — Two Connected Networks | router | 6 | – | NO3, NO9 | ok/ok/ok | ✅✅✅ |
| 21 | `rtr-edge-complete` — 10. Router — Edge Complete (capstone) | router | 7 | – | NO3, NO6, NO9 | ok/ok/ok | ✅✅✅ |
| 22 | `sw-hostname-write` — 11. Switch — Hostname and save | switch | 3 | – | NO9 | ok/ok/ok | ✅✅✅ |
| 23 | `rtr-hostname-write` — 12. Router — Hostname and save | router | 3 | – | NO9 | ok/ok/ok | ✅✅✅ |
| 24 | `w11-firewall` — Windows 11 VM — Firewall profiles | windows | 1 | – | CL3, CL6, IT10, IT13 | ok/ok/ok | ✅✅✅ |
| 25 | `w11-disk` — Windows 11 VM — List disks | windows | 1 | – | CL6, IT13, IT3 | ok/ok/ok | ✅✅✅ |
| 26 | `gui-devices` — Windows 11 GUI — Device Manager | win11gui | 3 | – | CL6, IT13, IT3 | ok/**fail**/ok | ✅✅✅ |
| 27 | `sw-port-security` — Switch — Port security on an access port | switch | 3 | – | NO2, NO5 | ok/ok/ok | ✅✅✅ |
| 28 | `rtr-default-route` — Router — Default route to the WAN | router | 4 | – | NO3 | ok/ok/ok | ✅✅✅ |
| 29 | `sw-banner` — Switch — Login banner | switch | 2 | – | NO2, NO5 | ok/ok/ok | ✅✅✅ |
| 30 | `w11-wlan` — Windows 11 VM — WLAN report | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 31 | `sw-mac-table` — Switch — MAC address table | switch | 2 | – | NO2 | ok/ok/ok | ✅✅✅ |
| 32 | `rtr-describe` — Router — Interface description | router | 3 | – | NO3 | ok/ok/ok | ✅✅✅ |
| 33 | `win-arp` — Windows 11 VM — ARP cache | windows | 2 | – | IT5, NO1 | ok/ok/ok | ✅✅✅ |
| 34 | `sw-int-status` — Switch — Interface status | switch | 2 | – | NO2, NO5 | ok/ok/ok | ✅✅✅ |
| 35 | `rtr-trace` — Router — Traceroute | router | 3 | – | NO3 | ok/ok/ok | ✅✅✅ |
| 36 | `win-route` — Windows 11 VM — Route table | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 37 | `win-getmac` — Windows 11 VM — MAC address | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 38 | `win-netstat` — Windows 11 VM — Active connections | windows | 1 | – | IT5, NO1 | ok/ok/ok | ✅✅✅ |
| 39 | `win-hostname` — Windows 11 VM — Hostname | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 40 | `win-ping-loop` — Windows 11 VM — Loopback ping | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 41 | `win-nslookup-ok` — Windows 11 VM — Working name lookup | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 42 | `win-flushdns` — Windows 11 VM — Flush DNS cache | windows | 1 | – | IT5 | ok/ok/ok | ✅✅✅ |
| 43 | `sw-show-ver` — Switch — show version | switch | 2 | – | NO2 | ok/ok/ok | ✅✅✅ |
| 44 | `sw-describe` — Switch — Access port description | switch | 2 | – | NO2 | ok/ok/ok | ✅✅✅ |
| 45 | `ticket-intake` — Block 1 — Ticket intake desk | ticket | 6 | – | IT1 | ok/ok/ok | ✅✅✅ |
| 46 | `hw-board` — Block 2 — Identify the board on the bench | ticket | 7 | – | IT2 | ok/ok/ok | ✅✅✅ |
| 47 | `net-subnet` 🆕 — Subnetting workbench — calculate, size and validate | activity | 4 | NO-1.2, IT-5.1 | IT5, NO1 | new/new/new | ✅✅✅ |
| 48 | `hw-cables` 🆕 — Connector and cable identification bench | activity | 3 | IT-3.4, NO-2.3 | IT3, NO2 | new/new/new | ✅✅✅ |
| 49 | `hw-pc-build` 🆕 — Workstation build — pick compatible parts | activity | 2 | IT-2.1, IT-2.2, IT-3.1, IT-3.3 | IT2, IT3 | new/new/new | ✅✅✅ |
| 50 | `ticket-method` 🆕 — Troubleshooting methodology — work a ticket end to end | activity | 6 | IT-7.1, IT-7.2, IT-7.3, IT-1.3, NO-6.1 | IT7, NO6 | new/new/new | ✅✅✅ |
| 51 | `win-net-cli` 🆕 — Windows CLI — isolate a name-resolution fault | windows | 10 | IT-5.3, IT-13.1, IT-13.2, NO-4.2 | CL6, IT13, IT5, NO4 | new/new/new | ✅✅✅ |
| 52 | `linux-shell` 🆕 — Linux shell — files, permissions and logs | linux | 8 | IT-9.1, IT-9.3 | CL2, IT9 | new/new/new | ✅✅✅ |
| 53 | `print-trouble` 🆕 — PowerShell — clear a stuck print queue | windows | 9 | IT-4.3, IT-13.1 | CL6, IT13, IT4 | new/new/new | ✅✅✅ |
| 54 | `rtr-vlan-acl` 🆕 — Router — inter-VLAN routing and a guest ACL | router | 9 | NO-2.2, NO-4.3, NO-5.3, NO-9.2 | NO4, NO5, NO9 | new/new/new | ✅✅✅ |
| 55 | `sw-vlan-multi` 🆕 — Switch — two VLANs, access ports and a pruned trunk | switch | 8 | NO-2.2, NO-9.1 | NO2, NO9 | new/new/new | ✅✅✅ |
| 56 | `wifi-secure` 🆕 — SOHO router — secure the admin page, Wi-Fi and guest network | activity | 4 | IT-5.4, NO-3.3, NO-5.2 | IT5, NO3, NO5 | new/new/new | ✅✅✅ |
| 57 | `sec-malware` 🆕 — Malware response — the seven-step removal process | activity | 5 | IT-10.2, IT-10.4 | CL3, IT10 | new/new/new | ✅✅✅ |
| 58 | `ops-backup` 🆕 — Backup and recovery — types, restore sets, 3-2-1, RPO/RTO | activity | 6 | IT-12.3, IT-3.2 | CL5, IT12 | new/new/new | ✅✅✅ |
| 59 | `virt-vm` 🆕 — Virtualization — build a Windows 11 lab VM | activity | 3 | IT-6.1, IT-6.3, IT-8.1 | IT6 | new/new/new | ✅✅✅ |
| 60 | `mob-mdm` 🆕 — Mobile devices — connectivity and MDM tickets inside policy | activity | 4 | IT-4.2, IT-1.4 | IT4 | new/new/new | ✅✅✅ |
| 61 | `win-ad-users` 🆕 — Active Directory Users and Computers — onboard, unlock, offboard | win11gui | 6 | IT-10.1, IT-8.4, IT-1.4 | CL1, CL3, IT10, IT8 | new/new/new | ✅✅✅ |
| 62 | `win-laptop-ports` 🆕 — Windows CLI — battery health, VM check, MX records and port tests | windows | 6 | IT-4.1, IT-5.1, IT-5.2, IT-6.1 | IT4, IT5, IT6 | new/new/new | ✅✅✅ |
| 63 | `win-wifi-survey` 🆕 — Windows CLI — Wi-Fi survey on a laptop (signal, band, channel) | windows | 6 | IT-5.4, NO-3.3 | IT5, NO3 | new/new/new | ✅✅✅ |
| 64 | `hv-vswitch` 🆕 — Hyper-V host — isolated virtual switch and checkpoints (PowerShell) | windows | 8 | IT-6.1, IT-6.3 | IT6 | new/new/new | ✅✅✅ |
| 65 | `linux-vm-perms` 🆕 — Real Linux VM — files, ownership, permissions and a support script | vm | 7 | IT-9.1, IT-9.3 | CL2, IT9 | new/new/new | ✅✅✅ |
| 66 | `linux-vm-shell` 🆕 — Real Linux VM — shell basics: files, permissions, scripts and logs | vm | 8 | IT-9.1, IT-9.3 | CL2, IT9 | new/new/new | ✅✅✅ |
| 67 | `linux-vm-services` 🆕 — Real Linux VM — services, processes, a filling disk, cron and syslog | vm | 8 | IT-9.1, NO-5.1 | CL2, IT9, NO5 | new/new/new | ✅✅✅ |
| 68 | `linux-vm-netclient` 🆕 — Real Linux VM — lease, gateway and name resolution on a live network | vm | 8 | IT-5.1, IT-5.3, IT-13.2, NO-4.1, NO-4.2 | CL6, IT13, IT5, NO4 | new/new/new | ✅✅✅ |
| 69 | `linux-vm-routing` 🆕 — Real Linux VMs — route between two networks (two machines, one router) | vm | 8 | NO-9.2, IT-5.1, IT-5.3 | IT5, NO9 | new/new/new | ✅✅✅ |
| – | `CL-4` — Print path and laptop FRU identification | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-6` — Build, snapshot and network a virtual machine | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-7` — Structured troubleshooting drills on staged faults | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-8` — Windows recovery ladder in a lab VM | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-9` — Linux command line and permissions | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-10` — Endpoint security posture check and incident tabletop | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-11` — Slow PC: resource tools and clean-boot isolation | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-12` — Change request and recovery drill | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |
| – | `CL-13` — PowerShell evidence and name-resolution repair | classroom (sign-off) | rubric | – | – | not recorded | ✅✅✅ |


## Findings by lab family (baseline → fix)

**Windows CLI** (win-ipconfig, win-dns-break, win-dhcp-renew, win-full-triage, w11-*, win-arp/route/getmac/netstat/hostname/ping-loop/nslookup-ok/flushdns)
- **What they do:** read identity and IP configuration, isolate DNS and DHCP faults, run netsh, services,
  processes, firewall and disk checks.
- **End-to-end:** they worked on desktop and phone, but progress was lost on reload, and there was no gradebook
  record and no instructor view.
- **Dead or unenforced steps:**
  - the renew order in win-dhcp-renew
  - in w11-wlan, the ticket's "connect" step could not be done because the simulator had no adapter profile
    (now covered by win-wifi-survey)
- **Commands added in this pass:** PowerShell aliases (`gip`, `gsv`, `gps`, `tnc`, `gc`), `ipconfig/all` without
  the space, `nslookup name server`, `Resolve-DnsName`, `Test-NetConnection -Port`, the printer cmdlets and
  `/?` usage. Anything else unknown gets a "Did you mean".
- **Unclear instructions:** none blocking. The objective texts now name the exact command.
- **Widths:** the baseline probe completed every one at 390 px, 820 px and desktop (16 px input, no overflow).
  The old page had no handling for the on-screen keyboard (no visualViewport sizing). Focus mode adds it.

**Windows 11 GUI** (gui-about, gui-ethernet, gui-renew, gui-services, gui-update, gui-accounts, gui-devices; new: win-ad-users)
- **Baseline:** completable on desktop and tablet only. At 390 px the Settings nav, the services list and the
  device tree were clipped or covered, and the probe's taps timed out on all 7 labs.
- **Bugs:**
  - gui-renew's Renew button does not exist in Windows 11
  - gui-update ticked its objective by opening the page, without checking for updates
- **Fixed:**
  - a server-driven event model
  - narrow mode and long-press
  - gui-update now requires "Check for updates"
  - gui-renew follows the real path

**IOS switch / router** (sw-*, rtr-*; new: sw-vlan-multi, rtr-vlan-acl)
- **Bugs:**
  - `ip route` from config-if was rejected
  - `sh int status` was ambiguous
  - descriptions and banners with spaces were mangled
  - pings left through shutdown interfaces
- **Unsupported (now added):** sub-interfaces and `encapsulation dot1Q`, ACLs, `switchport trunk allowed vlan`,
  `show access-lists`, `do` in config mode.
- **Widths:** OK at every width once focus mode was added. Long `show` output wraps.

**Ticket / bench** (ticket-intake, hw-board)
- **Baseline:** ticket-intake accepted any classification, and hw-board was missing from the index. Both are fixed.

**Classroom labs** (CL-4…CL-13)
- **Baseline:** listed in lesson plans only; no record anywhere.
- **Now:** a classroom page per lab, instructor sign-off (rubric levels 0–4 on four criteria → score), feedback
  shown to the student, and inclusion in the gradebook Labs column and the CSV.

## Known limits / next steps

- **Lab weight in the gradebook is 0 by default.** Sections opt in. The skills exams still assess the same
  stations summatively.
- **Concurrent requests for the same lab can race.** Last write wins. The terminal client queues its commands,
  so this matters only if a student has the same lab open in two tabs.
- **Real-VM labs are standard for the Linux and network-client skills, but two things are still open.** First,
  test them on physical phones; the figures above come from CPU-throttled Chromium. Second, build an
  institution-owned image (recipe in `docs/VM_IMAGE.md`) to meet the GPL source obligation and to unlock
  in-VM namespaces, bridges and VLANs. To turn a real lab off, remove it from `NEW_CHAPTER_LABS`. Its simulated
  fallback stays in place.
- **Simulated device output follows the real tools but is not exhaustive.** Unknown commands get "Did you mean"
  suggestions and a pointer to `help`.
