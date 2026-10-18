# Accuracy spot-check, round 2: 60 original items (Oct 18 2026)

Round 1 (40 items, `python tools/spot_check_sample.py 13`) is in `CURRICULUM_READINESS.md`. Round 2 draws 60 *other* original items (no certification items): `python tools/spot_check_sample.py --round2 14`. Every chapter of both courses gets at least one item, then one item per further objective, so the 60 items cover 60 different objectives.

The list checked is frozen in `docs/readiness/spot-check-round2-sample.json`. It was drawn on `content` before merging refinement pass 14. Pass 14 appended chapter-check items for IT-7.4 to IT-13.4, so re-running the command now gives a different list.

| Pool | Items |
|---|---|
| Passes 9–10 bank (`itsup_core.EXPANSION`) | 19 |
| ITSUP chapter checks | 13 |
| NETOPS chapter checks | 10 |
| question_bank A1 / A2 / N1 / N2 / N3 | 5 / 2 / 2 / 1 / 3 |
| Exam supplement | 5 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule, checked against the lesson that teaches it. **The checking was done by Grok Bot, not by an SME.** Every wording change below is marked *Pending SME review*.

## Result

- **60 checked, 0 wrong answer keys.** No key was changed.
- **4 stems fixed.**
  - A2.17 gave the answer away.
  - N1.20 had an ambiguous "shrinking windows".
  - NQ1.1 said a "frame crosses a router".
  - NQ4.5's wording also fitted PTR and SRV.
- **4 rationales rewritten or made precise:** X-IT-3.1.1, X-IT-13.2.1, N1.20 and NQ4.5.
- **12 ITSUP chapter-check items had a rationale that was only a section pointer.** Refinement pass 14 (`curriculum_v2/rationales_pass14.py`) covers these; see the post-merge note at the end.
- **1 item has an SME note and no change:** X-IT-11.4.3.

| Item | Before | After |
|---|---|---|
| A2.17 stem | "User cannot elevate with UAC while offline with cached creds for a domain account that requires online MFA for elevation. Explanation?" | "A domain laptop is offline. The user signs in with cached credentials, but every UAC elevation fails. Back on the office network, elevation works after an authenticator-app approval. What is the best explanation?" |
| N1.20 stem | "Packet capture shows retransmissions and shrinking windows during a file copy. Likely class of issue?" | "A packet capture of a slow file copy shows repeated TCP retransmissions, and the sender’s bytes in flight keep dropping. What class of issue is most likely?" (the rationale now also says a shrinking *receive* window alone points to the receiver) |
| NQ1.1 stem | "As a frame crosses a router, which value stays the same end to end (without NAT)?" | "As a packet crosses routers on its way to the destination, which value stays the same end to end (without NAT)?" |
| NQ4.5 stem | "Which DNS record type points one name to another name?" | "Which DNS record type makes one name an alias for another name?" |
| X-IT-3.1.1 rationale | "…RAID 1 adds redundancy, not speed." | names the seek time, says the PCIe adapter is an extra part, and says RAID 1 mirrors with at most a modest read gain |
| X-IT-13.2.1 rationale | "If the address is reachable, routing, the gateway and the lease work…" | "Reaching the server by address shows the adapter, the IP settings and the path to that host work…" (10.0.2.50 may be on the local subnet, so it proves nothing about the gateway) |

Where the changes are:
- `curriculum_v2/item_review.py`: A2.17 and N1.20, with `fix=` notes that say *Pending SME review*.
- `curriculum_v2/netops_checks.py`: NQ1.1 and NQ4.5, with comments.
- `curriculum_v2/itsup_core/ch03.py` and `ch13.py`: the EXPANSION rationales. These items already show *Pending SME review* in the LMS.

The tests are in `tests/test_spot_check_round2.py`.

## Items

| # | Item | Pool | Claim checked | Primary source | Verdict |
|---|---|---|---|---|---|
| 1 | S-IT-1.1.1 (IT-1.1) | exam_supplement | Many users lose a service → high-impact incident | ITIL 4 incident management (incident = unplanned interruption; impact by users affected) | Correct |
| 2 | Q1.5 (IT-1.2) | ITSUP chapter checks | Shock from a metal strip → classify as incident, stop, escalate | Course 1.2/1.5 (safety stop); OSHA electrical-hazard guidance | Correct. Rationale was only a pointer (see pass-14 rationales) |
| 3 | Q1.9 (IT-1.3) | ITSUP chapter checks | Closed = workflow works and notes complete | Course 1.1 (course rule) | Correct. Rationale was only a pointer |
| 4 | S-IT-1.4.2 (IT-1.4) | exam_supplement | Personal banking tab in a remote session → ask to close, do not record | CompTIA A+ 220-1102 obj. 4.7 (professionalism: confidential/private material) | Correct |
| 5 | Q2.1 (IT-2.1) | ITSUP chapter checks | LGA1700 silkscreen → lab command `socket lga1700` | `interactive_labs.py` bench lab (accepts `socket lga1700`; `form-factor` takes microatx) | Correct. Rationale was only a pointer |
| 6 | A1.5 (IT-2.2) | question_bank.A1 | Secure Boot blocks an unsigned loader → documented exception, then re-enable | UEFI spec 2.10 §32 (Secure Boot); NIST SP 800-147 (firmware change control) | Correct |
| 7 | A1.0 (IT-2.3) | question_bank.A1 | Continuous beep, fixed by reseating/testing sticks → memory module | Award/AMI beep-code tables (codes vary by vendor; isolation by stick is the evidence) | Correct |
| 8 | S-IT-2.4.2 (IT-2.4) | exam_supplement | Record model, serial, inventory → right part and before/after proof | Course 2.4; ITIL asset/configuration management | Correct |
| 9 | X-IT-3.1.1 (IT-3.1) | itsup_core.EXPANSION | SATA-only board → 2.5-inch SATA SSD is the biggest gain without parts | SATA-IO (SATA 6 Gb/s); M.2 needs a slot or PCIe adapter; RAID 1 read behaviour (Linux md(4)) | Key correct. **Rationale made precise**: it said RAID 1 adds "redundancy, not speed"; RAID 1 can give a modest read gain. Now names seek time, the adapter as an extra part, and the read gain |
| 10 | X-IT-3.3.1 (IT-3.3) | itsup_core.EXPANSION | Fans/LEDs but no POST → 8-pin EPS CPU power | ATX12V / EPS12V power supply design guide | Correct |
| 11 | X-IT-3.4.1 (IT-3.4) | itsup_core.EXPANSION | USB-C charges but no video → port lacks DP Alt Mode | VESA DisplayPort Alt Mode on USB Type-C | Correct |
| 12 | X-IT-4.1.1 (IT-4.1) | itsup_core.EXPANSION | Swollen Li-ion battery → stop using/charging, isolate | Manufacturer battery safety notices (Apple, Dell); CompTIA A+ 220-1101 obj. 1.1/5.x | Correct |
| 13 | X-IT-4.3.1 (IT-4.3) | itsup_core.EXPANSION | Every app on one PC fails, next desk prints → that PC's spooler/queue/driver | Course 4.3 (fault isolation); Microsoft print spooler troubleshooting | Correct |
| 14 | A1.12 (IT-5.3) | question_bank.A1 | LAN works, traceroute dies at gateway for names and IPs → upstream routing/NAT/firewall | RFC 792 (ICMP time exceeded) / traceroute behaviour | Correct |
| 15 | X-IT-5.4.2 (IT-5.4) | itsup_core.EXPANSION | Old and new devices on one SSID → WPA2/WPA3 transition mode | Wi-Fi Alliance WPA3 Specification v3 (WPA3-Personal transition mode) | Correct |
| 16 | X-IT-6.1.3 (IT-6.1) | itsup_core.EXPANSION | Container shares the host kernel; a VM does not | Linux namespaces(7)/cgroups(7); Docker overview | Correct |
| 17 | Q6.2 (IT-6.2) | ITSUP chapter checks | SaaS → you touch account, licence, client | NIST SP 800-145 (SaaS definition) | Correct. Rationale was only a pointer |
| 18 | X-IT-7.1.2 (IT-7.1) | itsup_core.EXPANSION | Three changes at once → cannot tell which fixed it | CompTIA A+ troubleshooting methodology (220-1102 obj. 4.10/5.1) | Correct |
| 19 | X-IT-7.2.1 (IT-7.2) | itsup_core.EXPANSION | Temporary profile on every PC → account or roaming profile | Microsoft Learn: troubleshoot temporary user profiles | Correct |
| 20 | Q7.8 (IT-7.3) | ITSUP chapter checks | Guesses labelled as guesses or left out | Course 7.3 / 1.3 (course rule) | Correct. Rationale was only a pointer |
| 21 | X-IT-7.4.2 (IT-7.4) | itsup_core.EXPANSION | Escalate early when the fix needs access/approval you lack | Course 7.4; ITIL functional escalation | Correct |
| 22 | Q8.0 (IT-8.1) | ITSUP chapter checks | Inventory name, edition and disks before install work | Course 8.1 / 2.6 (course rule) | Correct. Rationale was only a pointer |
| 23 | X-IT-8.2.3 (IT-8.2) | itsup_core.EXPANSION | Daily work as standard user → malware gets standard rights | NIST SP 800-53 AC-6(2); Microsoft UAC overview | Correct |
| 24 | X-IT-8.3.4 (IT-8.3) | itsup_core.EXPANSION | sfc cannot repair → DISM /RestoreHealth with a good source, then sfc | Microsoft Learn: Use System File Checker / Repair a Windows image | Correct |
| 25 | A1.29 (IT-8.4) | question_bank.A1 | Drive map for one AD group → GPP drive map (item-level targeting) | Microsoft Learn: Group Policy Preferences drive maps | Correct |
| 26 | Q9.1 (IT-9.1) | ITSUP chapter checks | sudo → administrative change for the record | sudo(8) man page; course rule | Correct |
| 27 | Q9.4 (IT-9.2) | ITSUP chapter checks | Swollen MacBook battery → stop, battery procedure | Apple: About lithium-ion batteries / service guidance | Correct. Rationale was only a pointer |
| 28 | X-IT-9.3.1 (IT-9.3) | itsup_core.EXPANSION | Colleague opens the share on the same device → user lacks access | Course 9.3 (isolation); Microsoft share/NTFS permissions docs | Correct |
| 29 | A2.17 (IT-10.1) | question_bank.A2 | Offline elevation fails, works online after an authenticator approval → elevation policy needs online MFA | Vendor docs for elevation MFA (e.g. Duo for Windows Logon offline access, EPM tools); Microsoft cached logon behaviour | Key correct. **Stem fixed**: the old stem said the account "requires online MFA for elevation", which is the answer. Now a scenario the student must interpret |
| 30 | Q10.7 (IT-10.2) | ITSUP chapter checks | Phish not opened → record it, confirm no credentials entered | NIST SP 800-61r2 (detection/analysis); course 10.4 | Correct. Rationale was only a pointer, and it points to 10.4 while the item is tagged IT-10.2 |
| 31 | Q10.6 (IT-10.3) | ITSUP chapter checks | Patch state is part of hygiene | NIST SP 800-40r4 (patch management) | Correct. Rationale was only a pointer |
| 32 | X-IT-10.4.3 (IT-10.4) | itsup_core.EXPANSION | Chain of custody = who held evidence, when, what they did | NIST SP 800-86 §3.1.1 / SP 800-72 | Correct |
| 33 | Q11.1 (IT-11.1) | ITSUP chapter checks | Exact error text belongs in the ticket | Course 11.1 (course rule) | Correct. Rationale was only a pointer |
| 34 | Q11.8 (IT-11.3) | ITSUP chapter checks | A reboot is treated as a change | Course 11.4 / 8.3 (course rule) | Correct. Rationale was only a pointer |
| 35 | X-IT-11.4.3 (IT-11.4) | itsup_core.EXPANSION | Temporary profile notice → record and escalate, do not delete | Microsoft Learn: temporary profile / ProfileList troubleshooting; course 11.4 escalation rule | Correct as a course rule. Note for SME: the distractor "Edit the ProfileList registry key yourself" is Microsoft's documented fix; it is wrong here only because the course makes it an endpoint-team task |
| 36 | A1.36 (IT-12.1) | question_bank.A1 | Unticketed production firewall change → change-management failure | ITIL 4 change enablement; NIST SP 800-53 CM-3 | Correct |
| 37 | A2.18 (IT-12.3) | question_bank.A2 | Strongest backup test → periodic test restore | NIST SP 800-34r1 §3.4 (testing) | Correct |
| 38 | X-IT-12.4.3 (IT-12.4) | itsup_core.EXPANSION | Usable runbook = numbered steps, prerequisites, results, rollback | Course 12.4; ITIL knowledge management | Correct |
| 39 | Q13.0 (IT-13.1) | ITSUP chapter checks | Chapter 13 = lab reps for skills already taught | Course chapter 13 overview | Correct. Rationale was only a pointer |
| 40 | X-IT-13.2.1 (IT-13.2) | itsup_core.EXPANSION | Reachable by IP, not by name → name resolution | RFC 1034/1035; Microsoft DNS client resolution order | Key correct. **Rationale made precise**: it said reaching the address proves "routing, the gateway and the lease" work; 10.0.2.50 may be on the local subnet, so it proves nothing about the gateway. Now: adapter, IP settings and the path to that host |
| 41 | X-IT-13.3.1 (IT-13.3) | itsup_core.EXPANSION | Before taskkill, record process, PID, hosted services | Microsoft Learn: tasklist /svc, taskkill | Correct |
| 42 | X-IT-13.4.2 (IT-13.4) | itsup_core.EXPANSION | Network reset → Wi-Fi, static and VPN settings may need redoing | Microsoft Support: Fix Wi-Fi connection issues in Windows, step 13 (network reset) | Correct |
| 43 | NQ1.1 (NO-1.1) | NETOPS chapter checks | Without NAT, the destination IP stays the same end to end | RFC 1812 §5.3.1, RFC 791 | Key correct. **Stem fixed**: "As a frame crosses a router" now reads "As a packet crosses routers…". A router ends each frame and builds a new one, which is the point of the item |
| 44 | NQ1.4 (NO-1.2) | NETOPS chapter checks | fe80::/10 = link-local | RFC 4291 §2.5.6 and §2.1 | Correct |
| 45 | NQ1.5 (NO-1.3) | NETOPS chapter checks | HTTPS = TCP 443 | IANA service-name registry; RFC 9110 | Correct |
| 46 | N3.3 (NO-2.1) | question_bank.N3 | LACP bundles links into one logical link | IEEE 802.1AX-2020 | Correct |
| 47 | NQ2.2 (NO-2.2) | NETOPS chapter checks | Port in VLAN 1 → assign it to VLAN 20 | IEEE 802.1Q; Cisco VLAN configuration guide | Correct |
| 48 | N1.27 (NO-3.2) | question_bank.N1 | VPC peering is non-transitive | AWS VPC Peering Guide (unsupported configurations: transitive peering, edge-to-edge routing) | Correct |
| 49 | NQ3.7 (NO-3.3) | NETOPS chapter checks | Per-user staff sign-in → WPA3-Enterprise with 802.1X | IEEE 802.1X; Wi-Fi Alliance WPA3 spec | Correct |
| 50 | N2.3 (NO-4.1) | question_bank.N2 | Rogue DHCP → addresses but sometimes the wrong gateway | RFC 2131 | Correct |
| 51 | NQ4.5 (NO-4.2) | NETOPS chapter checks | CNAME makes a name an alias | RFC 1035 §3.3.1; RFC 2782 (SRV target is a name); RFC 1035 §3.3.12 (PTR) | Key correct. **Stem fixed**: "points one name to another name" also fits PTR and SRV, whose data are names. Now asks for an alias. Rationale extended |
| 52 | N3.0 (NO-4.3) | question_bank.N3 | Established/related rule does not admit a new outbound flow | Netfilter conntrack documentation; stateful firewall behaviour | Correct |
| 53 | N3.2 (NO-5.1) | question_bank.N3 | WAN saturation → utilisation and drops over time | RFC 2863 (IF-MIB counters) | Correct |
| 54 | NQ5.5 (NO-5.2) | NETOPS chapter checks | Central logs with NTP → events can be correlated | RFC 5424 (syslog timestamps); NIST SP 800-92 | Correct |
| 55 | NQ5.7 (NO-5.3) | NETOPS chapter checks | Least privilege | NIST SP 800-53 AC-6 | Correct |
| 56 | N1.20 (NO-6.1) | question_bank.N1 | Retransmissions with falling bytes in flight → loss or congestion on the path | RFC 5681 (TCP congestion control); RFC 9293 | Key correct. **Stem and rationale fixed**: "shrinking windows" could mean the advertised receive window, which points to a slow receiver, not the path. Now "the sender's bytes in flight keep dropping" |
| 57 | NQ6.2 (NO-6.2) | NETOPS chapter checks | Two theories → test the most likely, least disruptive first, record | CompTIA Network+ N10-009 troubleshooting methodology (obj. 5.1) | Correct |
| 58 | S-NO-6.3.1 (NO-6.3) | exam_supplement | Proof of fix = the original failing test passes | CompTIA Network+ N10-009 obj. 5.1 (verify full functionality) | Correct |
| 59 | S-NO-9.1.2 (NO-9.1) | exam_supplement | `show interfaces trunk` shows allowed and active VLANs | Cisco Catalyst IOS command reference | Correct |
| 60 | NQ9.3 (NO-9.2) | NETOPS chapter checks | One router interface for VLANs 10 and 20 → router-on-a-stick with 802.1Q subinterfaces | Cisco IOS inter-VLAN routing configuration guide | Correct |

## After merging refinement pass 14

Refinement pass 14 is now merged into `content`. Twelve sampled ITSUP chapter-check items had a pointer rationale.

- **8 now have full rationales** from `rationales_pass14.py`: Q7.8, Q8.0, Q9.4, Q10.7, Q10.6, Q11.1, Q11.8 and Q13.0. I read all eight. They match the key and the course rules, and none contradicts its source.
  - Q10.7 still points to section 10.4 although the item is tagged IT-10.2.
  - Q13.0 says chapter 13 is "required rather than optional". That holds for the standard schedule, but `course_package.py` mentions a 3-credit variant that moves the chapter 13 reps.
- **4 still have a one-line "section — fragment" rationale:** Q1.5, Q1.9, Q2.1 and Q6.2. The pass-14 audit does not count these as pointer-only.
  - Across the whole ITSUP chapter-check bank, 61 of 144 items have a rationale like this: under 90 characters and starting with a section pointer.
  - They are thin rather than wrong. They are the next authoring job.

The merge dropped no items. Before and after the merge the item counts are equal: A1–N3 140; ITSUP checks 144, which is 130 plus the 14 pass-14 items; NETOPS checks 56; supplement 30; passes 9–10 bank 131; review entries 284; stem-guard mismatches 0.
