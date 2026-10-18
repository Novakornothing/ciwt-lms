# Accuracy spot-check, round 6: 60 original items (Oct 18 2026)

Rounds 1–5 are in `CURRICULUM_READINESS.md` and `docs/readiness/SPOT_CHECK_ROUND2.md` … `SPOT_CHECK_ROUND5.md`.
Round 6 draws 60 *other* original items (no certification items): `python tools/spot_check_sample.py --round6 18`.
Same method as rounds 3–5: it excludes the 40 round-1 ids (`ROUND1_IDS`) and the 240 ids frozen in
`docs/readiness/spot-check-round2-sample.json` … `spot-check-round5-sample.json`, plus X-IT-11.3.3 (`ROUND6_EXCLUDE`:
found outside the round-5 sample, stem tightened this round, on the SME list). Objectives checked least so far go
first, every chapter of both courses gets at least one item, and the 60 items cover 60 different objectives.

The list checked is frozen in `docs/readiness/spot-check-round6-sample.json`. It was drawn on `content` during content
round 6, after the round-6 tag work (tags change no item text) and the X-IT-11.3.3 edit (excluded from the draw).

| Pool | Items |
|---|---|
| itsup_core.EXPANSION | 17 |
| ITSUP chapter checks | 15 |
| NETOPS chapter checks | 6 |
| exam_supplement | 5 |
| question_bank.A1 | 5 |
| question_bank.N2 | 5 |
| question_bank.A2 | 3 |
| question_bank.N1 | 3 |
| question_bank.A3 | 1 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule, checked
against the lesson that teaches it. **The checking was done by Grok Bot, not by an SME.** Sources were checked from
the named documents as Grok Bot knows them; one claim with a recent date (WMIC removal, Q13.11) was re-checked live
against Microsoft Learn and Microsoft Support on Oct 18 2026.

## Result

- **60 checked. 0 answer keys changed. 0 stems changed. 0 options changed. 0 rationales changed.**
- **0 keys disputed in the sample.** All 60 items are correct as served; 3 of them carry SME / editor notes (below).
- **1 item outside the sample flagged for an SME: C-A1-3.5-3** (certification item, found while tagging; below). Not
  changed, not tagged.
- Tests: `tests/test_spot_check_round6.py`.

### Notes for an SME or editor (no change made)
- **A1.2 (dual-channel), wording only.** The stem reads "A workstation with dual-channel capable board … after a
  upgrade". The key is right; the stem is missing "a" before "dual-channel" and should read "after an upgrade". Not
  changed: wording, not accuracy, and the question bank text is shared by the CLIENT package.
- **A2.15 (split pairs), item construction.** The stem names the fault ("reports split pairs") and the key restates it
  ("Split pairs despite correct pin continuity"), so the item tests recognition of the phrase rather than the concept.
  The key and rationale are right (split pairs pass wire map / continuity and fail NEXT). Suggested rewrite: describe
  the certifier result ("wire map passes, NEXT fails on two pairs") and ask for the fault.
- **A1.19 (HTTPS test), stem scope.** The stem asks to confirm the host "accepts HTTPS only". Connecting to TCP 443 and
  checking the certificate proves HTTPS is offered, not that plain HTTP (TCP 80) is refused. The key is still the best
  of the four options (none of the others tests either). Suggested: drop "only", or add "and that TCP 80 is closed or
  redirects" to the key.

### Outside the sample: C-A1-3.5-3 (ARM laptop, possible outdated key)
- **Item.** "A user’s new laptop has an ARM processor and an old accounting app will not install. What is the most
  likely reason?" Key: "The app is built only for x86/x64 processors." Explanation: "Software must be built for the CPU
  architecture or run under emulation."
- **Problem.** Windows 11 on Arm runs most x86 and x64 desktop apps under emulation (Microsoft Learn, "Windows on Arm"
  / "How emulation works on Arm"), so "built only for x86/x64" alone does not usually stop an install. Old apps more
  often fail on Arm because they need a kernel-mode driver (for example a licence dongle or a printer driver), which
  emulation does not cover. The key is the closest of the four options (TPM, core count and Secure Boot are clearly
  wrong), so it is not clearly wrong, but the explanation should say why emulation did not help.
- **Not changed, not tagged.** Suggested: "The app (or a driver it installs) is built only for x86/x64, and drivers
  are not emulated on Arm", with the rationale naming kernel drivers.

## Items

| # | Item | Pool | Claim checked | Primary source | Verdict |
|---|---|---|---|---|---|
| 1 | S-IT-1.1.2 (IT-1.1) | exam_supplement | Planned laptop + mailbox for a new starter → service request | ITIL 4 Service request management practice (request vs incident) | Correct |
| 2 | Q2.2 (IT-2.1) | ITSUP checks | DDR5 label → lab command `memory ddr5`; DDR4 keyed differently | Course hw-board bench card (lesson 2.4 command list); JEDEC DDR4 and DDR5 DIMM standards (key-notch positions) | Correct |
| 3 | A1.2 (IT-2.3) | question_bank.A1 | Two modules in slots 1 and 2 share a channel → move to the named pair | Motherboard vendor manuals (DIMM population tables, e.g. A2/B2); course 2.3 | Correct (editor note) |
| 4 | Q3.1 (IT-3.1) | ITSUP checks | Only `list disk` is non-destructive; clean/delete/convert change disks | Microsoft Learn, diskpart command reference (list disk, clean, delete partition, convert gpt); course 3.1 | Correct |
| 5 | X-IT-3.2.3 (IT-3.2) | EXPANSION | Incremental restore = full + every incremental in order | NIST SP 800-34 Rev. 1 (full, incremental, differential backups) | Correct |
| 6 | A2.1 (IT-3.3) | question_bank.A2 | Power-hungry GPU on an unpowered riser → too little slot power, artefacts | PCI Express CEM specification (slot power limit, 75 W x16); GPU vendor riser guidance | Correct |
| 7 | A2.15 (IT-3.4) | question_bank.A2 | Split pairs: continuity correct, pairs mixed, NEXT fails | ANSI/TIA-568.2-D (wire map, NEXT); ANSI/TIA-1152-A field testers | Correct (SME note) |
| 8 | A1.4 (IT-4.1) | question_bank.A1 | Fault that follows lid angle → hinge cable or connector | Laptop vendor service manuals (display/DC-in cable routed through the hinge) | Correct |
| 9 | Q4.3 (IT-4.2) | ITSUP checks | Work profile / MDM = shop-managed enrolment, not sidestepped | Microsoft Learn, Intune enrolment and compliance; Apple Platform Deployment (device management) | Correct |
| 10 | X-IT-4.3.2 (IT-4.3) | EXPANSION | Stop Print Spooler before deleting files in spool\PRINTERS | Microsoft Learn, Print Spooler service; Microsoft Support, clearing stuck print jobs | Correct |
| 11 | X-IT-5.1.4 (IT-5.1) | EXPANSION | fe80::/10 is link-local; fd00::/8 ULA; 2001:db8::/32 documentation; ::ffff: mapped | IETF RFC 4291; RFC 4193; RFC 3849 | Correct |
| 12 | A1.19 (IT-5.2) | question_bank.A1 | HTTPS = TCP 443; connect and check the certificate | IANA service names and ports (https 443/tcp); RFC 9110 | Correct (SME note) |
| 13 | A2.16 (IT-5.3) | question_bank.A2 | Switch-dependent teaming without matching switch config → unstable aggregate | Microsoft Learn, NIC Teaming (switch-dependent modes need switch configuration); IEEE 802.1AX (LACP) | Correct |
| 14 | Q5.8 (IT-5.4) | ITSUP checks | Changing a shared AP admin password is a change under shop process | Course 5.4 / 1.3 (change rule); ITIL 4 Change enablement | Correct |
| 15 | S-IT-6.1.1 (IT-6.1) | exam_supplement | Type 1 hypervisor runs on hardware without a host OS | NIST SP 800-125 (hypervisor types) | Correct |
| 16 | X-IT-6.2.3 (IT-6.2) | EXPANSION | Measured service is a NIST essential characteristic | NIST SP 800-145 | Correct |
| 17 | Q6.7 (IT-6.3) | ITSUP checks | No guest adapter / APIPA with host network up → hypervisor owner (vNIC, port group, uplink) | Microsoft Learn, Hyper-V virtual switch; VMware vSphere networking; course 6.3 | Correct |
| 18 | S-IT-7.1.1 (IT-7.1) | exam_supplement | After the fix: verify full functionality, then document | CompTIA A+ troubleshooting methodology (competency standard); course 7.1 | Correct |
| 19 | Q7.6 (IT-7.2) | ITSUP checks | Ping by IP works, by name fails → name resolution (DNS) | IETF RFC 1034/1035 (name resolution); course 7.2 / 5.3 | Correct |
| 20 | X-IT-7.3.3 (IT-7.3) | EXPANSION | Closure note: cause, fix, verification, prevention | ITIL 4 Incident management (closure records); course 7.3 | Correct |
| 21 | Q7.10 (IT-7.4) | ITSUP checks | "Current state" is the escalation part that says what was changed | Course 7.4 escalation package (six parts) | Correct |
| 22 | Q8.1 (IT-8.1) | ITSUP checks | MEM beep, no video → POST memory; reinstall cannot fix it | Motherboard vendor manuals (POST / debug LEDs); course 8.1 / 2.5 | Correct |
| 23 | Q8.5 (IT-8.2) | ITSUP checks | DHCP Client service stopped → no lease (APIPA or failed renewals) | Microsoft Learn, DHCP Client service (registers and renews addresses); RFC 2131 | Correct |
| 24 | X-IT-8.3.1 (IT-8.3) | EXPANSION | Run DISM /RestoreHealth before sfc /scannow | Microsoft Support, "Use the System File Checker tool to repair missing or corrupted system files" | Correct |
| 25 | Q8.10 (IT-8.4) | ITSUP checks | Local, site, domain, OU: OU GPO applied later wins unless enforced/blocked | Microsoft Learn, Group Policy processing order and precedence | Correct |
| 26 | X-IT-9.1.3 (IT-9.1) | EXPANSION | Owner rw, group r, others none = 640 | POSIX chmod (IEEE Std 1003.1, octal modes) | Correct |
| 27 | X-IT-9.2.1 (IT-9.2) | EXPANSION | Apple silicon: hold the power button for startup options; Command-R is Intel | Apple Support, "Start up your Mac in macOS Recovery" | Correct |
| 28 | S-IT-9.3.2 (IT-9.3) | exam_supplement | Server reachable, "permission denied" on a file → access/permissions | POSIX (EACCES); Linux open(2) manual page | Correct |
| 29 | X-IT-9.4.3 (IT-9.4) | EXPANSION | "bad interpreter" from a Windows-edited script → CRLF line endings | Linux execve(2) manual page (#! interpreter line); course 9.4 | Correct |
| 30 | X-IT-10.1.3 (IT-10.1) | EXPANSION | Named admin accounts make privileged changes traceable | NIST SP 800-53 Rev. 5 AC-2, IA-2 (unique identification, accountability) | Correct |
| 31 | X-IT-10.2.2 (IT-10.2) | EXPANSION | Defender Offline runs outside Windows to catch hiding malware | Microsoft Learn, "Run and review the results of a Microsoft Defender Offline scan" | Correct |
| 32 | A1.33 (IT-10.3) | question_bank.A1 | Suspended BitLocker leaves a clear key on disk until resumed | Microsoft Learn, Suspend-BitLocker (clear key) | Correct |
| 33 | A3.9 (IT-10.4) | question_bank.A3 | Directory-service change auditing records who changed a GPO | Microsoft Learn, "Audit Directory Service Changes" (event 5136) | Correct |
| 34 | Q11.0 (IT-11.1) | ITSUP checks | Only Outlook fails; Word and the next desk work → one app on one PC | Course 11.1 scope table | Correct |
| 35 | X-IT-11.2.3 (IT-11.2) | EXPANSION | msconfig Safe boot persists until unticked | Microsoft Support, "Start your PC in safe mode in Windows" (System Configuration) | Correct |
| 36 | X-IT-11.3.2 (IT-11.3) | EXPANSION | Rebuild plan starts with a backup and a tested restore | Course 11.3 ("A rebuild is a change", step 1); NIST SP 800-34 Rev. 1 | Correct |
| 37 | X-IT-11.4.2 (IT-11.4) | EXPANSION | Memory that climbs and never drops → leak in that process | Microsoft Learn, memory leak diagnosis (Performance Monitor private bytes) | Correct |
| 38 | X-IT-12.1.2 (IT-12.1) | EXPANSION | Backout plan = tested steps to undo, with a trigger | ITIL 4 Change enablement (remediation / backout) | Correct |
| 39 | Q12.2 (IT-12.2) | ITSUP checks | A password never goes in a ticket | NIST SP 800-63B (do not disclose authenticators); course 12.2 | Correct |
| 40 | A1.46 (IT-12.3) | question_bank.A1 | One deleted file on a healthy volume → restore that file (backup / Previous Versions) | Microsoft Support, "Restore previous versions of files"; NIST SP 800-34 Rev. 1 | Correct |
| 41 | X-IT-12.4.1 (IT-12.4) | EXPANSION | KB article includes verification steps; never secrets or personal data | ITIL 4 Knowledge management; course 12.4 | Correct |
| 42 | Q13.9 (IT-13.1) | ITSUP checks | Chapter 13 bar: labs submitted, notes meet the Block 1 bar | Course 13.6 pass bar | Correct |
| 43 | X-IT-13.2.3 (IT-13.2) | EXPANSION | After a hosts fix: flush the cache, resolve again | Microsoft Learn, ipconfig /flushdns and Resolve-DnsName | Correct |
| 44 | Q13.7 (IT-13.3) | ITSUP checks | List processes before a reboot (a reboot destroys the evidence) | Course 13.6 / 8.3; Microsoft Learn, tasklist | Correct |
| 45 | Q13.11 (IT-13.4) | ITSUP checks | WMIC removed from Windows 11 24H2 and later; Get-NetIPConfiguration summarises IP, gateway, DNS | Microsoft Learn, "Features and functionality removed in Windows client" (WMIC, August 2026) and Microsoft Support WMIC removal timeline (checked live Oct 18 2026); Microsoft Learn, Get-NetIPConfiguration | Correct |
| 46 | N2.9 (NO-1.2) | question_bank.N2 | /28 → 16 addresses, 14 usable | IETF RFC 4632; RFC 950 | Correct |
| 47 | NQ1.7 (NO-1.3) | NETOPS checks | SNMP polling UDP 161; traps 162; syslog 514 | IETF RFC 3417 (SNMP transport mappings); IANA ports | Correct |
| 48 | N2.6 (NO-2.1) | question_bank.N2 | BPDU Guard err-disables an edge port that receives BPDUs | Cisco Catalyst, "Configuring Optional Spanning-Tree Features" (BPDU Guard) | Correct |
| 49 | NQ2.6 (NO-2.3) | NETOPS checks | 400 m at 10 Gb/s → fibre (10GBASE-SR OM4 ~400 m; copper 100 m) | IEEE 802.3 Clause 52 (10GBASE-SR reach); ANSI/TIA-568.2-D (100 m channel) | Correct |
| 50 | N2.7 (NO-3.1) | question_bank.N2 | Dual-homed BGP: routes via the failed provider are withdrawn; traffic follows the other | IETF RFC 4271 (BGP-4 route withdrawal) | Correct |
| 51 | N1.16 (NO-3.2) | question_bank.N1 | Tunnel up, traffic not matching → selectors and routes into the tunnel | IETF RFC 7296 (IKEv2 traffic selectors); RFC 4301 | Correct |
| 52 | N2.2 (NO-4.2) | question_bank.N2 | AAAA maps a name to IPv6 | IETF RFC 3596 | Correct |
| 53 | N1.14 (NO-4.3) | question_bank.N1 | DMZ separates Internet-facing services from internal networks | NIST SP 800-41 Rev. 1 (DMZ) | Correct |
| 54 | N1.28 (NO-5.1) | question_bank.N1 | Logs only on each device: no central, tamper-resistant store | NIST SP 800-92 (log management, centralisation) | Correct |
| 55 | N2.17 (NO-5.2) | question_bank.N2 | CoPP protects the device CPU from control-plane floods | IETF RFC 6192 (protecting the router control plane); Cisco CoPP guide | Correct |
| 56 | NQ5.6 (NO-5.3) | NETOPS checks | Guest VLAN/zone with an Internet-only policy | NIST SP 800-153 (WLAN security, guest segmentation); course NETOPS 5.3 | Correct |
| 57 | NQ6.0 (NO-6.1) | NETOPS checks | One building affected → what those users share (uplink, gateway) | Course NETOPS 6.1 scope rule; CompTIA Network+ troubleshooting methodology (competency standard) | Correct |
| 58 | NQ6.3 (NO-6.2) | NETOPS checks | Time boxes force escalate / roll back decisions | Course NETOPS 6.2; ITIL 4 Major incident management | Correct |
| 59 | S-NO-9.1.1 (NO-9.1) | exam_supplement | `switchport access vlan 30` assigns an access port | Cisco IOS interface configuration (switchport access vlan) | Correct |
| 60 | NQ9.7 (NO-9.2) | NETOPS checks | Connected route "C" appears once the subinterface is addressed and up | Cisco IOS `show ip route` (route codes) | Correct |
