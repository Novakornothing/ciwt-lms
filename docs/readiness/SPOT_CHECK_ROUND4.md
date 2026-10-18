# Accuracy spot-check, round 4: 60 original items (Oct 18 2026)

Rounds 1–3 are in `CURRICULUM_READINESS.md`, `docs/readiness/SPOT_CHECK_ROUND2.md` and `docs/readiness/SPOT_CHECK_ROUND3.md`.
Round 4 draws 60 *other* original items (no certification items): `python tools/spot_check_sample.py --round4 16`. Same
method as round 3: it excludes the 40 round-1 ids (`ROUND1_IDS`) and the 120 ids frozen in
`docs/readiness/spot-check-round2-sample.json` and `spot-check-round3-sample.json`; objectives checked least so far go
first, every chapter of both courses gets at least one item, and the 60 items cover 60 different objectives.

The list checked is frozen in `docs/readiness/spot-check-round4-sample.json`. It was drawn on `content` after the
round-4 rationale and tag commits (`fa0fa2f`, `fd31dc0`), and items were read as the engine serves them. Two sampled
items (Q1.6, Q6.0) carry a rationale written earlier in this round; their keys are original.

| Pool | Items |
|---|---|
| ITSUP chapter checks | 25 |
| itsup_core.EXPANSION | 11 |
| question_bank.A1 | 8 |
| question_bank.N1 | 6 |
| NETOPS chapter checks | 4 |
| exam_supplement | 2 |
| question_bank.N2 | 2 |
| question_bank.A3 | 1 |
| question_bank.A2 | 1 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule, checked
against the lesson that teaches it. **The checking was done by Grok Bot, not by an SME.**

## Result

- **60 checked. 0 answer keys changed. 0 stems changed. 0 rationales changed.**
- **1 key disputed, not changed: Q9.11** (below). The evidence that the key is inaccurate comes from Samba community
  sources and user tests, not from official documentation, so under the round rule (no key change without a clear
  primary source) it goes to an SME.
- 58 items correct as served; 4 of them carry SME notes.
- One lesson fact outside the sample was corrected (AM5 socket type, below), *Pending SME review*.
- Tests: `tests/test_spot_check_round4.py`.

### Q9.11: key disputed (no change made)
- **Item.** "A Linux share holds both Plan.docx and plan.docx. What does a Windows user browsing the share usually
  see?" Key: "Only one, as Windows treats names case-insensitively by default." Lesson 9.4's scenario says the same
  ("Windows … shows only one of them").
- **What the sources say.**
  - Samba `smb.conf(5)`, *case sensitive*: the default `auto` is the same as `no` for Windows clients, and Samba
    then resolves a name the client passes by a caseless search.
  - On *listing*, a Samba mailing-list explanation (samba@lists.samba.org, March 2001) and user tests
    (for example `dir` from Windows on a Raspberry Pi Samba share) report that Explorer and `dir` **list both
    names**. Opening either one opens the same file, the first caseless match.
- **So** the user's real symptom is "I open plan.docx and get the other file's contents", which matches the lesson's
  "keeps changing to old numbers" story. But "shows only one" is probably wrong for what a user *sees* in the folder.
  The distractor "Both files, listed side by side…" may be the more accurate statement of the listing.
- **Suggested fix for an SME** (needs a test on a real Windows client against Samba first). Change the stem to "A
  Windows user opens plan.docx from the share. What can happen?" with the key "They may get Plan.docx instead,
  because Windows matches names case-insensitively". Change the lesson clause to "lists both but opens whichever
  matches first".

### Notes for an SME (no change made)
- **Q8.3 (key wording).** The key "A pending update is a change window" does not answer "why read Windows Update on a
  reboot loop?" directly; the rationale does ("a pending or failed update can restart the PC repeatedly"). A clearer
  key would be "A pending or failed update can cause the restarts". The key's meaning, as the rationale explains it,
  is right.
- **X-IT-5.3.1 (ICMP).** "Valid lease, cannot ping the gateway → check the local LAN and gateway" is the right next
  step in the course order. Some gateways and firewalls do not answer ICMP echo, so a failed gateway ping is strong
  evidence but not proof. Lesson 5.3 could say so in one clause.
- **A1.48 (Sysprep).** Generalising (Sysprep `/generalize`) gives each clone a new SID and, with an answer file, a
  new name. A static IP address baked into the image still has to be changed. The explanation already says "plus
  unique names and addresses".
- **Q1.6 and Q12.0** test the same fact with almost the same stem ("production DNS after 1500 against policy"), on
  IT-1.1 and IT-12.1. That is fine for spaced review. A student who learns the answer once gets mastery evidence on
  two objectives from one memory.

### Citation erratum (rounds 3 and 4)
CompTIA's 220-1201 exam objectives say the troubleshooting methodology "does not constitute a formal objective or part
of the A+ certification exam" in the 220-1200 series. It appears as a competency-standard section, and objective 5.1 is
"troubleshoot motherboards, RAM, CPUs, and power". Earlier text cited it as "220-1201 objective 5.1". That was correct
for 220-1101, not for 220-1201. Fixed in:
- three round-3 misconception sources (`misconceptions_round3.py`)
- the round-4 sources for Q7.0 and Q7.3

`SPOT_CHECK_ROUND3.md` is left as the round-3 record. Its rows for A1.38, A3.0 and X-IT-7.1.1 have the same
mis-citation, and their verdicts are unaffected. Network+ N10-009 objective 5.1 *is* the methodology, and those citations
stand.

### Lesson correction found while writing round-4 rationales (outside the sample)
- **AM5 socket type (lessons 2.1 and 2.3, `block2_hardware.py`).** Before: "AMD AM4/AM5: pins on the CPU" and
  "AM4/AM5: pins on the chip". AMD's Socket AM5 quick reference guide says "1718-pin LGA socket": AM5 CPUs have
  pads, and the pins are in the socket, as on Intel LGA. Now: "AMD AM4: pins on the CPU. AMD AM5 is an LGA socket
  too (LGA1718: pads on the CPU, pins in the socket)" and "AM4: pins on the chip; do not set it on a screw. AM5 is
  LGA, like Intel: protect the socket pins." *Pending SME review.* No item key depends on it.

## Items

| # | Item | Pool | Claim checked | Primary source | Verdict |
|---|---|---|---|---|---|
| 1 | Q1.6 (IT-1.1) | ITSUP checks | Adding a production DNS record against policy is a change | ITIL 4 Change enablement (a change adds, modifies or removes something that could affect services); course 1.3 | Correct. SME note (near-duplicate of Q12.0) |
| 2 | A1.37 (IT-1.2) | question_bank.A1 | Grounded wrist strap + ESD mat; not contacts, plastic bag or rubber soles | CompTIA A+ Core 2 (220-1202) operational procedures, ESD; ANSI/ESD S20.20 (grounding of personnel and work surfaces) | Correct |
| 3 | Q1.3 (IT-1.3) | ITSUP checks | Usable note = version, error, tests with results, start time | Course 1.3 note standard; ITIL 4 Incident management (records) | Correct |
| 4 | S-IT-1.4.1 (IT-1.4) | exam_supplement | Verify identity with the approved method before a reset | NIST SP 800-63B-4 (account recovery requires identity proofing); CISA social-engineering guidance | Correct |
| 5 | Q2.3 (IT-2.1) | ITSUP checks | Short M.2 slot on the card = storage nvme | Course hw-board bench card (lesson 2.5: "NVMe in the short slot") | Correct |
| 6 | A1.1 (IT-2.2) | question_bank.A1 | Firmware sees the NVMe, installer does not → RAID/VMD mode needs a driver | Intel VMD/RST documentation (load the VMD driver in Windows Setup); Microsoft Learn, Windows Setup load-driver | Correct |
| 7 | Q3.7 (IT-2.3) | ITSUP checks | Long beeps + MEM, no video → POST memory, not the display cable | Board vendor manuals (DRAM debug LED); course 2.5 POST table | Correct |
| 8 | Q2.7 (IT-2.4) | ITSUP checks | list disk shows which handle is the OS disk before imaging | Microsoft Learn, diskpart list disk / select disk | Correct |
| 9 | Q3.0 (IT-3.1) | ITSUP checks | NVMe is a protocol that often uses the M.2 slot | NVM Express Base Specification; PCI-SIG M.2 (form factor carries SATA or PCIe) | Correct |
| 10 | Q3.3 (IT-3.2) | ITSUP checks | RAID 0 loses the volume when one disk dies | Patterson, Gibson & Katz 1988 (RAID 0 has no redundancy); SNIA Dictionary, RAID 0 | Correct |
| 11 | Q3.9 (IT-3.3) | ITSUP checks | Four changes at once → you cannot tell what fixed it | CompTIA A+ 220-1201 exam objectives, troubleshooting methodology section (test one theory at a time; competency standard, not a tested objective) | Correct |
| 12 | Q3.6 (IT-3.4) | ITSUP checks | POST OK, dark panel → cable and input first | Course 3.4 display isolation order; Microsoft Support, black-screen troubleshooting | Correct |
| 13 | X-IT-4.1.2 (IT-4.1) | EXPANSION | powercfg /batteryreport shows design and full-charge capacity | Microsoft Learn, powercfg command-line options (/batteryreport) | Correct |
| 14 | X-IT-4.2.3 (IT-4.2) | EXPANSION | Cellular works, office Wi-Fi fails → check SSID and address | Course 4.2 isolation table (guest SSID, portal, proxy) | Correct |
| 15 | Q4.4 (IT-4.3) | ITSUP checks | One app on one PC fails, Word works → that app/driver path | Microsoft Support, "Fix printer connection and printing problems in Windows"; course 4.3 | Correct |
| 16 | A1.21 (IT-5.1) | question_bank.A1 | Link-local IPv6 only → no RA or DHCPv6 address | IETF RFC 4861 (router advertisements), RFC 4862 (SLAAC), RFC 8415 (DHCPv6) | Correct |
| 17 | Q5.6 (IT-5.2) | ITSUP checks | Ping to the mail server IP works → not the NIC | Course 5.2/5.3 isolation order (a working IP path rules out link and NIC) | Correct |
| 18 | X-IT-5.3.1 (IT-5.3) | EXPANSION | Valid lease, gateway ping fails → local LAN and gateway next | Course 5.3 isolation order; CompTIA Network+ N10-009 obj. 5.1 | Correct. SME note (ICMP filtering) |
| 19 | A1.17 (IT-5.4) | question_bank.A1 | ISP uses DHCP, router set static → set WAN to obtain automatically | IETF RFC 2131 (DHCP client); SOHO router vendor WAN-setup guides | Correct |
| 20 | Q6.0 (IT-6.1) | ITSUP checks | A VM is a guest made of files running on a host | NIST SP 800-125 (host, hypervisor, guest) | Correct (round-4 rationale) |
| 21 | Q6.3 (IT-6.2) | ITSUP checks | Whole tenant fails, laptop IP fine → vendor/tenant path | NIST SP 800-145 (SaaS: provider manages the application); course 6.2 | Correct |
| 22 | A1.48 (IT-6.3) | question_bank.A1 | Clones clash on name and IP → generalise (Sysprep) | Microsoft Learn, Sysprep overview (/generalize removes computer-specific information such as the SID) | Correct. SME note (static IP) |
| 23 | Q7.9 (IT-7.2) | ITSUP checks | diskpart during a SaaS outage crosses fault domains | Course 7.2 / 7.4 (fault domains) | Correct |
| 24 | A1.49 (IT-7.3) | question_bank.A1 | Escalating without steps tried → tier 2 repeats work | ITIL 4 Incident management (escalation with information); CompTIA A+ 220-1202 obj. 4.1 | Correct |
| 25 | X-IT-7.4.3 (IT-7.4) | EXPANSION | Status updates at an agreed interval, even with no change | ITIL 4 Incident management (communication); CompTIA A+ 220-1202 obj. 4.7 (set and meet expectations) | Correct |
| 26 | Q8.2 (IT-8.1) | ITSUP checks | Clean wipes the OS volume; in-place keeps apps and files | Microsoft Support, "Reinstall Windows" and "Fix issues by reinstalling the current version of Windows" | Correct |
| 27 | Q8.3 (IT-8.2) | ITSUP checks | Read Windows Update on a reboot loop: a pending update explains it | Microsoft Support, Windows Update troubleshooting (restarts to finish installing); course 8.2 | Correct. SME note (key wording) |
| 28 | X-IT-8.3.3 (IT-8.3) | EXPANSION | Reliability Monitor (perfmon /rel) shows crashes beside installs | Microsoft Learn, Reliability Monitor (perfmon /rel) | Correct |
| 29 | A1.28 (IT-8.4) | question_bank.A1 | 10-minute skew, intermittent logons → Kerberos clock-skew limit | Microsoft Learn, "Maximum tolerance for computer clock synchronization" (default 5 minutes) | Correct |
| 30 | Q9.7 (IT-9.2) | ITSUP checks | About This Mac ↔ Settings → System → About | Apple Support, "About This Mac"; Microsoft Support, "Find your Windows version" (Settings > System > About) | Correct |
| 31 | Q9.5 (IT-9.3) | ITSUP checks | Access never held → service request / entitlement | ITIL 4 Service request management; course 1.1 / 9.3 | Correct |
| 32 | Q9.11 (IT-9.4) | ITSUP checks | Linux share with Plan.docx and plan.docx: Windows "shows only one" | Samba smb.conf(5), "case sensitive" (auto = no for Windows clients; Samba resolves a passed name by caseless match). Listing behaviour: Samba mailing-list explanation (2001) and user tests: Explorer lists both, opening either opens the first match | **Key disputed, not changed.** See below |
| 33 | A1.44 (IT-10.2) | question_bank.A1 | Many internal sources failing logons on one account → protect it and follow the incident process | NIST SP 800-61 Rev. 3 (detection and response); Microsoft Learn, event 4625 auditing | Correct |
| 34 | A3.5 (IT-10.3) | question_bank.A3 | Allow-listing blocks unauthorised programs such as ransomware | NIST SP 800-167, Guide to Application Whitelisting | Correct |
| 35 | X-IT-10.4.1 (IT-10.4) | EXPANSION | After a phish: check the mailbox for new forwarding rules | Microsoft Learn, "Responding to a compromised email account" (inbox and forwarding rules, sessions, MFA) | Correct |
| 36 | X-IT-11.1.1 (IT-11.1) | EXPANSION | Application Error, event ID 1000 records a crash with the faulting module | Microsoft Learn / Windows event reference (Application Error 1000; Kernel-Power 41 = unexpected shutdown) | Correct |
| 37 | Q11.4 (IT-11.2) | ITSUP checks | Repair or in-place upgrade before a rebuild | Microsoft Support, "Recovery options in Windows"; course 11.3 / 8.1 | Correct |
| 38 | A2.6 (IT-11.3) | question_bank.A2 | A locked log file → stop the owning service gracefully, then manage the file | Microsoft Learn, Resource Monitor (associated handles) and service control | Correct |
| 39 | X-IT-11.4.1 (IT-11.4) | EXPANSION | Slow "Applying user settings" → GroupPolicy Operational log and gpresult /h | Microsoft Learn, Group Policy troubleshooting (Microsoft-Windows-GroupPolicy/Operational; gpresult) | Correct |
| 40 | Q12.0 (IT-12.1) | ITSUP checks | Production DNS after 1500 against policy is a change | ITIL 4 Change enablement; course 12.1 / 1.3 | Correct |
| 41 | X-IT-12.2.3 (IT-12.2) | EXPANSION | Possible crime: stop, record facts, report through the procedure | CompTIA A+ 220-1202 obj. 4.6 (prohibited content: report through proper channels, preserve evidence, chain of custody) | Correct |
| 42 | Q12.4 (IT-12.3) | ITSUP checks | RAID and snapshots are not off-site copies | CISA, "Back Up Business Data" (3-2-1); Broadcom KB 1025279 (snapshots are not backups) | Correct |
| 43 | X-IT-12.4.2 (IT-12.4) | EXPANSION | Disposed asset: status disposed with date and sanitisation reference | NIST SP 800-88 Rev. 2 (sanitization records / certificate) | Correct |
| 44 | Q13.2 (IT-13.1) | ITSUP checks | ipconfig /all output goes in the ticket as evidence | Course 13.2 / 5.1 evidence rule; Microsoft Learn, ipconfig | Correct |
| 45 | Q13.5 (IT-13.2) | ITSUP checks | The firewall stays on during 13.4 | Course 13.4 (stated lab rule); Microsoft Learn, Windows Firewall (keep enabled) | Correct |
| 46 | Q13.1 (IT-13.3) | ITSUP checks | Inventory the lab VM before changing it | Course 13.1 / 2.6 | Correct |
| 47 | X-IT-13.4.1 (IT-13.4) | EXPANSION | Renew fails after a desk move, other ports work → known-good port, escalate the bad one | Course 13.4 / 5.3 isolation order | Correct |
| 48 | N1.21 (NO-1.1) | question_bank.N1 | ARP maps IPv4 addresses to MAC addresses | IETF RFC 826 | Correct |
| 49 | NQ1.3 (NO-1.2) | NETOPS checks | Broadcast of 172.16.5.64/27 is .95 | IETF RFC 950 / RFC 4632 (block of 32: .64–.95) | Correct |
| 50 | N1.1 (NO-1.3) | question_bank.N1 | Live voice/video prefers UDP | IETF RFC 3550 (RTP over UDP); RFC 768 | Correct |
| 51 | N1.15 (NO-2.2) | question_bank.N1 | 802.1Q carries VLAN identity on trunks | IEEE 802.1Q | Correct |
| 52 | N2.16 (NO-2.3) | question_bank.N2 | 10GBASE-T fails past the 100 m channel / with lower categories | IEEE 802.3an (10GBASE-T, 100 m on Cat 6A; ~55 m on Cat 6); ANSI/TIA-568.2-D | Correct |
| 53 | N2.18 (NO-3.1) | question_bank.N2 | traceroute / tracert shows the hops | Microsoft Learn, tracert; traceroute(8) | Correct |
| 54 | N1.22 (NO-3.3) | question_bank.N1 | Busy 2.4 GHz → move capable clients to 5/6 GHz, cut overlap | IEEE 802.11 channel plan (three non-overlapping 20 MHz channels in 2.4 GHz); Cisco/Aruba WLAN design guides | Correct |
| 55 | NQ4.0 (NO-4.1) | NETOPS checks | DORA: Discover, Offer, Request, Acknowledge | IETF RFC 2131 §3.1 | Correct |
| 56 | N1.19 (NO-5.3) | question_bank.N1 | Zero trust: verification and least privilege everywhere | NIST SP 800-207, Zero Trust Architecture | Correct |
| 57 | N1.10 (NO-6.1) | question_bank.N1 | One VLAN fails through a shared core → compare routing, ACL and NAT per VLAN | CompTIA Network+ N10-009 obj. 5.1 (question the obvious, compare what differs) | Correct |
| 58 | NQ6.5 (NO-6.2) | NETOPS checks | Status update = impact, current action, next update time | ITIL 4 Incident management (communication) | Correct |
| 59 | NQ6.7 (NO-6.3) | NETOPS checks | After the incident update diagrams, configs and the runbook | CompTIA Network+ N10-009 obj. 5.1 (document findings, actions and outcomes) | Correct |
| 60 | S-NO-9.2.2 (NO-9.2) | exam_supplement | show ip interface brief lists addresses and up/down status | Cisco IOS command reference, show ip interface brief | Correct |
