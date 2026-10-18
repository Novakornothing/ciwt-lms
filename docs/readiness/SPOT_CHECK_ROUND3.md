# Accuracy spot-check, round 3: 60 original items (Oct 18 2026)

Round 1 (40 items) is in `CURRICULUM_READINESS.md` and round 2 (60 items) in `docs/readiness/SPOT_CHECK_ROUND2.md`.
Round 3 draws 60 *other* original items (no certification items): `python tools/spot_check_sample.py --round3 15`.
It excludes the 40 round-1 ids (frozen in `ROUND1_IDS`, because `sample(13)` no longer reproduces round 1 after pass 14
added chapter-check items) and the 60 round-2 ids (read from `docs/readiness/spot-check-round2-sample.json`). The
objectives checked least so far go first, every chapter of both courses gets at least one item, and the 60 items cover
60 different objectives.

The list checked is frozen in `docs/readiness/spot-check-round3-sample.json`. It was drawn on `content` after merging
refinement `f9ffdc4` (pass 15). Items were read as the engine serves them (after the item review, pass 14/15
rationales and pass 15 option-length rewrites).

| Pool | Items |
|---|---|
| ITSUP chapter checks | 18 |
| Passes 9–10 bank (`itsup_core.EXPANSION`) | 15 |
| NETOPS chapter checks | 10 |
| question_bank A1 / A2 / A3 / N1 / N2 / N3 | 5 / 2 / 2 / 2 / 2 / 2 |
| Exam supplement | 2 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule, checked
against the lesson that teaches it. **The checking was done by Grok Bot, not by an SME.** The one wording change is
marked *Pending SME review*.

## Result

- **60 checked, 0 wrong answer keys. No key was changed.**
- **1 stem fixed: X-IT-9.2.3.** "remove the college’s management profile from *their* Mac" reads as a personally owned
  Mac, and then the key's "device owner" would be the user. The stem now says "the college-owned Mac they use", and the
  rationale ends "here the owner is the college". Key and distractors unchanged. (`curriculum_v2/itsup_core/ch09.py`.)
- **0 rationales were wrong.** Two are thin and two have SME notes (below).
- Tests: `tests/test_spot_check_round3.py`.

| Item | Before | After |
|---|---|---|
| X-IT-9.2.3 stem | "A user asks you to remove the college’s management profile from their Mac because it blocks an app. What do you do?" | "A user asks you to remove the management profile from the college-owned Mac they use, because it blocks an app. What do you do?" |
| X-IT-9.2.3 rationale | "…changing them is the device owner’s decision." | "…changing them is the device owner’s decision, and here the owner is the college." |

### Notes for an SME (no change made)
- **X-IT-6.3.3 (Paused-Critical).** The key ("the host volume is almost out of space") is right. The rationale, the
  lesson 6.3 text and the glossary all say the volume "holding the VM’s disks". Microsoft also names the volume holding
  the checkpoint (snapshot) files, which can be a different drive (Microsoft Learn, "Virtual machines enter paused
  state", KB 2486243; Checkpoints and Snapshots Overview FAQ). Worth one clause in the lesson.
- **X-IT-8.1.1 ("Fix problems using Windows Update").** The key is right (Microsoft Support, "Fix issues by reinstalling
  the current version of Windows": reinstalls the same version and keeps apps, files and settings). Microsoft hides the
  option on PCs whose updates are managed (work or school). Lesson 8.1 already says so; the item does not, so on a
  managed college PC a student may never see the option.
- **Thin rationales.** Q1.0 ("1.1 — new access is a request, not a repair.") and Q2.5 ("2.2 — a wrong boot order looks
  like a dead OS.") are correct but do not explain the key. Measured across the served bank, **23 ITSUP chapter-check
  items** still have a rationale under 90 characters that starts with a section pointer: Q1.0, Q1.1, Q1.5, Q1.6, Q1.8,
  Q2.0, Q2.1, Q2.2, Q2.4, Q2.5, Q2.6, Q2.8, Q4.0, Q4.2, Q4.3, Q4.6, Q5.7, Q6.0, Q6.1, Q6.6, Q6.7, Q7.0, Q7.3. Pass 15's
  full rationales apply only where an item had no review rationale of its own, and these 23 carry their study tip as
  that rationale, so they kept the one-liner. They pass the readiness rule (at least 10 words).

## Items

| # | Item | Pool | Claim checked | Primary source | Verdict |
|---|---|---|---|---|---|
| 1 | Q1.0 (IT-1.1) | ITSUP checks | New access never held → service request | ITIL 4 Service request management (request for access/information, not a failure) | Correct. Thin rationale |
| 2 | Q1.4 (IT-1.2) | ITSUP checks | Power off, unplug, wait, strap on skin, then open | CompTIA A+ Core 2 operational procedures, safety (ESD strap on skin, disconnect power first); course 1.2 | Correct |
| 3 | A1.38 (IT-1.3) | question_bank.A1 | "Internet is slow" → ask scope, start time, wired/wireless, changes | CompTIA A+ 220-1201 obj. 5.1 step 1 (question the user, determine what changed) | Correct |
| 4 | Q1.7 (IT-1.4) | ITSUP checks | Ticket holds facts, times, tests, next step; never the password | Course 1.4; NIST SP 800-53 IA-5 (protect authenticator content from disclosure) | Correct |
| 5 | Q2.5 (IT-2.2) | ITSUP checks | UEFI runs before Windows to check hardware and start boot | UEFI Specification 2.10 (boot services before ExitBootServices) | Correct. Thin rationale |
| 6 | A3.0 (IT-2.3) | question_bank.A3 | Onboard video works once the GPU is out → GPU or its slot/power path | CompTIA A+ 220-1201 obj. 5.1 (test the theory by isolation) | Correct |
| 7 | Q2.9 (IT-2.4) | ITSUP checks | About RAM < DIMMs fitted → seating or firmware first | Course 2.6; board vendor memory-detection guidance | Correct |
| 8 | A2.0 (IT-3.1) | question_bank.A2 | Rising reallocated sectors → migrate and replace | SMART attribute 05 (Reallocated Sectors Count); Microsoft Learn, Optimize Drives (SSDs are trimmed, not defragmented) | Correct |
| 9 | X-IT-3.2.4 (IT-3.2) | EXPANSION | RAID 5 degraded → confirm a restorable backup before touching disks | RAID 5 tolerates one failed disk, so a degraded array has no redundancy left (Patterson, Gibson & Katz 1988); NAS vendor degraded-volume guidance (back up before repair) | Correct |
| 10 | A1.9 (IT-3.3) | question_bank.A1 | Thick paste blob → clean, thin layer, reseat | Intel and AMD processor/cooler installation guides | Correct |
| 11 | X-IT-3.4.3 (IT-3.4) | EXPANSION | Dark display after POST, power and input checked → swap cable/adapter | Course 3.4 (display isolation order) | Correct |
| 12 | Q4.9 (IT-4.1) | ITSUP checks | Portable pass bar = a note a peer can act on | Course 4.4 / Block 1 note standard | Correct |
| 13 | Q4.8 (IT-4.2) | ITSUP checks | gui-accounts teaches: check who is signed in first | Course 4.2 lab (`interactive_labs.py` gui-accounts) | Correct |
| 14 | A1.13 (IT-5.1) | question_bank.A1 | 25 hosts → /27 (30 usable); /28 holds 14 | RFC 950; RFC 4632 §3.1 | Correct |
| 15 | Q5.5 (IT-5.2) | ITSUP checks | Port 53 = DNS; 587 submission, 80/443 web, 3389 RDP | IANA Service Name and Port Number Registry; RFC 1035; RFC 6409 | Correct |
| 16 | X-IT-5.4.3 (IT-5.4) | EXPANSION | `netsh wlan show interfaces` shows SSID, signal, authentication | Microsoft Learn, Netsh commands for WLAN (`show interfaces`) | Correct |
| 17 | X-IT-6.1.2 (IT-6.1) | EXPANSION | "Virtualization: Disabled" → enable VT-x/AMD-V in UEFI | Microsoft Learn, Enable virtualization on Windows (firmware setting) | Correct |
| 18 | Q6.4 (IT-6.2) | ITSUP checks | In IaaS the customer still owns the guest OS | NIST SP 800-145 §2 (IaaS: consumer controls operating systems) | Correct |
| 19 | X-IT-6.3.3 (IT-6.3) | EXPANSION | Paused-Critical → host volume almost out of space | Microsoft Learn KB 2486243, "Virtual machines enter paused state" | Correct. SME note (checkpoint volume) |
| 20 | X-IT-7.1.1 (IT-7.1) | EXPANSION | Run the quick, safe test that could rule out the top theory first | CompTIA A+ 220-1201 obj. 5.1 (establish and test a theory) | Correct |
| 21 | X-IT-7.2.2 (IT-7.2) | EXPANSION | Fails at one site, works from home → site path, proxy or DNS | Course 7.2 (scope by what the affected users share) | Correct |
| 22 | Q12.9 (IT-7.3) | ITSUP checks | Chapter 12 bar: peer can tell the domain, safety stops held | Course 12.4 | Correct |
| 23 | Q7.11 (IT-7.4) | ITSUP checks | On escalation tell the user who has it, what is needed, next update | ITIL 4 Incident management (communication); course 7.4 | Correct |
| 24 | X-IT-8.1.1 (IT-8.1) | EXPANSION | "Fix problems using Windows Update" keeps apps, files, settings; Reset this PC removes apps and settings | Microsoft Support, "Fix issues by reinstalling the current version of Windows"; "Recovery options in Windows" | Correct. SME note (managed PCs) |
| 25 | A1.20 (IT-8.2) | question_bank.A1 | Ping works, RDP fails after firewall → inbound TCP 3389 rule | Microsoft Learn, Remote Desktop (TCP 3389) and Windows Firewall inbound rules | Correct |
| 26 | Q8.6 (IT-8.3) | ITSUP checks | List processes before a reboot "to clear it" | Course 8.3; RFC 3227 §2.1 (volatile data first) | Correct |
| 27 | Q8.11 (IT-8.4) | ITSUP checks | `gpresult /r` lists applied and filtered-out GPOs | Microsoft Learn, gpresult command reference | Correct |
| 28 | A3.6 (IT-9.1) | question_bank.A3 | Use sudo only for commands that need it | sudo(8) and sudoers(5) man pages; NIST SP 800-53 AC-6 | Correct |
| 29 | X-IT-9.2.3 (IT-9.2) | EXPANSION | Decline removing the MDM profile; the owner decides | Apple Platform Deployment, device management profiles; course 9.2 | Key correct. **Stem fixed** (ownership) |
| 30 | X-IT-9.3.3 (IT-9.3) | EXPANSION | Never ask for, type or record a user's password | NIST SP 800-53 IA-5; course 1.4 / 9.3 | Correct |
| 31 | Q9.10 (IT-9.4) | ITSUP checks | macOS reads NTFS but does not write it natively | Apple Support, Disk Utility file system formats (NTFS read-only) | Correct |
| 32 | Q10.9 (IT-10.2) | ITSUP checks | Chapter 10 bar: factual note, no password, Defender on | Course 10.4 | Correct |
| 33 | A1.35 (IT-10.3) | question_bank.A1 | Restrict kiosk USB → endpoint policy blocking removable media | NIST SP 800-53 MP-7 (Media Use) | Correct |
| 34 | S-IT-11.1.1 (IT-11.1) | exam_supplement | Every user's app fails after an update → the app/update | Course 11.1 (scope) | Correct |
| 35 | Q11.5 (IT-11.2) | ITSUP checks | Before a rebuild: backup, change ticket, list disk | Course 11.3; ITIL 4 Change enablement | Correct |
| 36 | A2.8 (IT-11.3) | question_bank.A2 | Storage bottleneck → high latency and queue, modest CPU | Microsoft Learn, disk performance counters (Avg. Disk sec/Transfer, queue length) | Correct |
| 37 | Q11.10 (IT-11.4) | ITSUP checks | Fault gone in Safe Mode → a driver, service or startup item | Microsoft Support, "Start your PC in safe mode" (limited set of files and drivers) | Correct |
| 38 | X-IT-12.1.3 (IT-12.1) | EXPANSION | Block a phishing domain in minutes → emergency change, reviewed after | ITIL 4 Change enablement (emergency changes: expedited authorisation) | Correct |
| 39 | S-IT-12.2.1 (IT-12.2) | exam_supplement | Possible AUP breach found → stop and report via policy | CompTIA A+ Core 2 operational procedures (prohibited content: report through proper channels) | Correct |
| 40 | X-IT-12.3.1 (IT-12.3) | EXPANSION | RAID 1 is not a backup: deletions/corruption hit both disks | NIST SP 800-34 Rev. 1 (redundancy vs backup) | Correct |
| 41 | Q12.10 (IT-12.4) | ITSUP checks | KB title in the user's words, describing the symptom | Consortium for Service Innovation, KCS v6 Practices Guide (capture in the requestor's context) | Correct |
| 42 | X-IT-13.1.1 (IT-13.1) | EXPANSION | WMIC removed → `Get-CimInstance Win32_BIOS` for the serial | Microsoft Support, "WMIC removal from Windows" (removed from Windows 11 24H2/25H2 from the August 2026 update); Win32_BIOS SerialNumber | Correct |
| 43 | X-IT-13.3.3 (IT-13.3) | EXPANSION | A pending update requiring restart justifies a restart now | Course 13.3 (evidence before restart) | Correct |
| 44 | X-IT-13.4.3 (IT-13.4) | EXPANSION | `Test-NetConnection server -Port 443` tests TCP 443 | Microsoft Learn, Test-NetConnection (-Port, TcpTestSucceeded) | Correct |
| 45 | NQ1.0 (NO-1.1) | NETOPS checks | Ping by IP works, by name fails → name resolution (application layer) | RFC 1123 / RFC 1035 (DNS is an application protocol) | Correct |
| 46 | N3.5 (NO-1.2) | question_bank.N3 | IPv6 needs no NAT: enough global addresses, still firewalled | RFC 4864 | Correct |
| 47 | NQ1.6 (NO-1.3) | NETOPS checks | DNS queries use UDP: small, retried on loss; large replies/zone transfers TCP | RFC 1035 §4.2; RFC 7766 | Correct |
| 48 | NQ2.0 (NO-2.1) | NETOPS checks | Unknown unicast flooded in the VLAN except the source port | IEEE 802.1Q (forwarding process, unknown destination flooding) | Correct |
| 49 | NQ2.4 (NO-2.2) | NETOPS checks | Native VLAN frames are sent untagged | IEEE 802.1Q (PVID / untagged frames); Cisco trunk configuration guide | Correct |
| 50 | N2.5 (NO-2.3) | question_bank.N2 | Single-mode for long runs between buildings | ANSI/TIA-568.3-D (fibre channel distances) | Correct |
| 51 | N2.11 (NO-3.3) | question_bank.N2 | OFDMA → efficiency serving many clients at once | IEEE 802.11ax-2021 (OFDMA resource units) | Correct |
| 52 | NQ4.2 (NO-4.1) | NETOPS checks | DHCP option 3 = router (gateway); 6 DNS, 15 domain, 51 lease | RFC 2132 §3.5, §3.8, §3.17, §9.2 | Correct |
| 53 | NQ4.6 (NO-4.3) | NETOPS checks | Many hosts share one address by source port → PAT | RFC 3022 (NAPT) | Correct |
| 54 | NQ5.0 (NO-5.1) | NETOPS checks | Syslog 2 (critical) is more severe than 5 (notice) | RFC 5424 §6.2.1, Table 2 | Correct |
| 55 | N1.25 (NO-5.3) | question_bank.N1 | Unauthorised devices on access ports → 802.1X | IEEE 802.1X-2020 | Correct |
| 56 | N1.26 (NO-6.1) | question_bank.N1 | PMTUD black hole → large transfers stall, small packets work | RFC 1191; RFC 2923 §2.1 | Correct |
| 57 | N3.8 (NO-6.2) | question_bank.N3 | Changing three variables at once → cannot attribute the result | CompTIA Network+ N10-009 obj. 5.1 (one change at a time) | Correct |
| 58 | NQ6.6 (NO-6.3) | NETOPS checks | Verify: re-run the failing test, confirm with users | CompTIA Network+ N10-009 obj. 5.1 (verify full system functionality) | Correct |
| 59 | NQ9.2 (NO-9.1) | NETOPS checks | `show interfaces trunk` lists allowed and active VLANs | Cisco Catalyst configuration guide, VLAN trunks (`show interfaces trunk`) | Correct |
| 60 | NQ9.4 (NO-9.2) | NETOPS checks | IOS default route `ip route 0.0.0.0 0.0.0.0 203.0.113.1` | Cisco IOS IP Routing configuration guide, static routes | Correct |
