# Accuracy spot-check, round 5: 60 original items (Oct 18 2026)

Rounds 1–4 are in `CURRICULUM_READINESS.md` and `docs/readiness/SPOT_CHECK_ROUND2.md` … `SPOT_CHECK_ROUND4.md`.
Round 5 draws 60 *other* original items (no certification items): `python tools/spot_check_sample.py --round5 17`. Same
method as rounds 3–4: it excludes the 40 round-1 ids (`ROUND1_IDS`) and the 180 ids frozen in
`docs/readiness/spot-check-round2-sample.json`, `spot-check-round3-sample.json` and `spot-check-round4-sample.json`;
objectives checked least so far go first, every chapter of both courses gets at least one item, and the 60 items cover
60 different objectives.

The list checked is frozen in `docs/readiness/spot-check-round5-sample.json`. It was drawn on `content` during content
round 5; round 5 changed no item text (it added misconception tags only), so items were read as the engine serves them.

| Pool | Items |
|---|---|
| itsup_core.EXPANSION | 18 |
| ITSUP chapter checks | 17 |
| NETOPS chapter checks | 10 |
| exam_supplement | 6 |
| question_bank.N1 | 3 |
| question_bank.N2 | 3 |
| question_bank.A1 | 2 |
| question_bank.A2 | 1 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule, checked
against the lesson that teaches it. **The checking was done by Grok Bot, not by an SME.**

## Result

- **60 checked. 0 answer keys changed. 0 stems changed. 0 options changed. 0 rationales changed.**
- **0 keys disputed in the sample.** 60 items correct as served; 2 of them carry SME notes (below).
- **1 item outside the sample flagged for an SME: X-IT-11.3.3** (possible second correct option, below). Not changed.
- Tests: `tests/test_spot_check_round5.py`.

### Notes for an SME (no change made)
- **X-IT-8.3.2 (System Restore).** The key is right: Microsoft's "Recovery options in Windows" says restoring from a
  system restore point does not affect personal files. The scenario assumes a restore point from before Tuesday
  exists. That needs System Protection to be turned on for the system drive, which is not the case on every PC. A
  clause in the stem ("System Protection is on") would remove the assumption.
- **NQ2.1 (STP wording).** The key (a layer-2 loop causing a broadcast storm) is right. The rationale says "without STP
  edge protection (BPDU Guard) broadcasts multiply". Spanning tree itself blocks a loop like this; BPDU Guard
  error-disables an edge port that receives BPDUs. The storm happens when spanning tree is off or bypassed (for example
  an unmanaged switch in the path). Suggested wording: "with spanning tree off or bypassed, broadcasts multiply; BPDU
  Guard on edge ports shuts the port instead."

### Outside the sample: X-IT-11.3.3 (possible second correct option)
- **Item.** "When is a rebuild a poor choice even though repair is slow?" Key: "When there is no tested backup of the
  user’s data." Distractor: "When the fault has a known, documented vendor fix."
- **Problem.** The item's own explanation ends "a documented fix would also favour repair". So a student who picks the
  distractor has a defensible answer, and the explanation agrees with them.
- **Found** while tagging the X-IT bank in this round (the item is left untagged for that reason).
- **Not changed.** Changing an option is an item rewrite that an SME should approve. Suggested fix: replace the
  distractor with one that is clearly wrong, for example "When the device is under warranty", and drop the last clause
  of the explanation, or turn the item into a choose-two.

## Items

| # | Item | Pool | Claim checked | Primary source | Verdict |
|---|---|---|---|---|---|
| 1 | Q1.8 (IT-1.1) | ITSUP checks | Half the badges down + warm reader → incident, impact many, escalate | Course lab ticket-intake (lesson 1.5 command list); ITIL 4 Incident management (impact, escalation) | Correct |
| 2 | Q1.2 (IT-1.4) | ITSUP checks | Verify identity under shop policy before a password reset | NIST SP 800-63B-4 (identity verification before authenticator reset/recovery); course 1.1/1.4 | Correct |
| 3 | A1.6 (IT-2.1) | question_bank.A1 | x16 card in an electrically x4 slot works at x4 bandwidth | PCI Express Base Specification, link training and width negotiation (LTSSM) | Correct |
| 4 | Q2.6 (IT-2.2) | ITSUP checks | Secure Boot = firmware starts only a signed bootloader | UEFI Specification 2.10, Secure Boot and Driver Signing; Microsoft Learn, "Secure boot" | Correct |
| 5 | Q2.4 (IT-2.3) | ITSUP checks | MEM debug LED + long beeps, no video → post memory | Course hw-board bench card (lesson 2.5 POST table); motherboard vendor manuals (DRAM/MEM debug LED) | Correct |
| 6 | S-IT-2.4.1 (IT-2.4) | exam_supplement | Reported RAM below installed → seating, detection or a failed module | Course lesson for IT-2.4 (inventory reconciliation); motherboard vendor manuals (memory detection, QVL) | Correct |
| 7 | X-IT-3.1.2 (IT-3.1) | EXPANSION | M.2 2280 = 22 mm wide, 80 mm long | PCI-SIG M.2 specification (form-factor naming 2230/2242/2280) | Correct |
| 8 | X-IT-3.2.1 (IT-3.2) | EXPANSION | Four 4 TB disks in RAID 5 → 12 TB usable | SNIA Common RAID Disk Data Format (DDF) specification, RAID-5 (one disk of parity) | Correct |
| 9 | X-IT-3.3.3 (IT-3.3) | EXPANSION | Ride through outages and shut down cleanly → UPS with a shutdown signal | IEC 62040-3 (UPS); UL 1449 (surge protective devices do not supply power) | Correct |
| 10 | Q4.1 (IT-4.1) | ITSUP checks | Under-rated brick → slow charging or CPU throttling | USB-IF USB PD power rules; laptop vendor adapter guidance (read both labels); course 4.1 | Correct |
| 11 | Q4.2 (IT-4.2) | ITSUP checks | Works on cellular, fails on building Wi-Fi → isolate WLAN/portal/proxy, no factory reset | Course 4.2 isolation table; Microsoft Learn, Intune wipe/retire | Correct |
| 12 | Q4.6 (IT-4.3) | ITSUP checks | Print path: app → spooler → driver/port → link → device | Microsoft Support, "Fix printer connection and printing problems in Windows"; Microsoft Learn, Print Spooler service | Correct |
| 13 | X-IT-5.1.1 (IT-5.1) | EXPANSION | /27 → 32 addresses, 30 usable | IETF RFC 4632 (CIDR); RFC 950 (network and broadcast addresses) | Correct |
| 14 | X-IT-5.2.3 (IT-5.2) | EXPANSION | MX lists a domain’s mail servers; PTR reverse, CNAME alias | IETF RFC 1035 (MX, PTR, CNAME); RFC 3596 (AAAA) | Correct |
| 15 | X-IT-5.4.1 (IT-5.4) | EXPANSION | Default admin credentials are the biggest hole; hidden SSID/MAC filtering are not controls | CISA, "Home Network Security" and "Securing Wireless Networks" (change default credentials) | Correct |
| 16 | Q6.5 (IT-6.1) | ITSUP checks | A snapshot is a restore point for a change, not a backup | Microsoft Learn, Hyper-V checkpoints; Broadcom KB 1025279 (snapshots are not backups); NIST SP 800-125 | Correct |
| 17 | S-IT-6.2.1 (IT-6.2) | exam_supplement | Hosted email, customer manages users and settings → SaaS | NIST SP 800-145 (service models) | Correct |
| 18 | Q7.0 (IT-7.1) | ITSUP checks | Process starts with identify (who, what, how many, safety) | CompTIA A+ 220-1201 troubleshooting methodology section (competency standard, not a tested objective), step 1; course 7.1 | Correct |
| 19 | Q7.3 (IT-7.3) | ITSUP checks | Verified = the outcome the user called about works | ITIL 4 Incident management (closure confirmed with the user); course 7.3 | Correct |
| 20 | X-IT-7.4.1 (IT-7.4) | EXPANSION | Escalation package: impact, scope, evidence, actions tried, request | ITIL 4 Incident management (escalation with information); course 7.4 | Correct |
| 21 | X-IT-8.1.3 (IT-8.1) | EXPANSION | Out-of-service Windows version → no more security updates; Home/Pro 24 months, Enterprise/Education 36 | Microsoft Learn, Windows lifecycle FAQ and Windows 11 release information | Correct |
| 22 | Q8.7 (IT-8.2) | ITSUP checks | Firewall profile stays on for a game launcher; admin or snapshot do not change that | Microsoft Learn, Windows Firewall (rules and exceptions instead of disabling a profile); course 8.3 | Correct |
| 23 | X-IT-8.3.2 (IT-8.3) | EXPANSION | System Restore to a point before the driver install keeps personal files | Microsoft Support, "Recovery options in Windows" (System Restore does not affect personal files) | Correct. SME note (restore point must exist) |
| 24 | X-IT-8.4.1 (IT-8.4) | EXPANSION | Kerberos fails beyond the default 5-minute clock skew | Microsoft Learn, "Maximum tolerance for computer clock synchronization" (default 5 minutes) | Correct |
| 25 | X-IT-9.1.1 (IT-9.1) | EXPANSION | -rw-r----- → group may read only | Linux man-pages, chmod(1) and ls(1) (symbolic mode triplets) | Correct |
| 26 | S-IT-9.2.2 (IT-9.2) | exam_supplement | Managed Mac gets profiles and apps through the organisation’s MDM | Apple Platform Deployment guide (MDM payloads and app distribution) | Correct |
| 27 | S-IT-9.3.1 (IT-9.3) | exam_supplement | Access denied while group colleagues succeed → group membership and share permissions | Microsoft Learn, share and NTFS permissions; Apple Support, connecting to SMB shares | Correct |
| 28 | X-IT-9.4.2 (IT-9.4) | EXPANSION | Mac connects to \\files\budget with Finder → Go → Connect to Server → smb://files/budget | Apple Mac User Guide, "Connect to a Windows computer from a Mac" (Connect to Server, smb://) | Correct |
| 29 | X-IT-10.2.3 (IT-10.2) | EXPANSION | Do not reimage before security review: evidence of entry is lost | NIST SP 800-61 Rev. 3 (preserve evidence for analysis); CISA #StopRansomware Guide | Correct |
| 30 | A1.39 (IT-10.3) | question_bank.A1 | Finance drives leaving service → cryptographic erase or destruction per policy | NIST SP 800-88 Rev. 2 (purge: cryptographic erase; destroy) | Correct |
| 31 | X-IT-10.4.2 (IT-10.4) | EXPANSION | RFC 3227: memory and process table before disk, remote logs, archives | IETF RFC 3227 section 2.1 (order of volatility) | Correct |
| 32 | Q11.2 (IT-11.1) | ITSUP checks | IP works, name fails → DNS domain | Microsoft Learn, DNS client troubleshooting (nslookup, Resolve-DnsName); course 5.3/11.2 | Correct |
| 33 | Q11.6 (IT-11.2) | ITSUP checks | One crashing app → isolate the app before a clean image | Course 11.3 repair-or-rebuild table; Microsoft Support, repair or reset apps | Correct |
| 34 | X-IT-11.3.1 (IT-11.3) | EXPANSION | Several unrelated faults past the time box → planned rebuild with backup and app list | Course chapter 11, "Repair, reinstall or rebuild?" and "Time boxes protect the user’s day" (course procedure) | Correct |
| 35 | Q11.11 (IT-11.4) | ITSUP checks | Store app Repair keeps the app’s data; Reset deletes it | Microsoft Support, "Repair apps and programs in Windows" (Repair: data not affected; Reset: data deleted) | Correct |
| 36 | A2.14 (IT-12.1) | question_bank.A2 | Risky step at 03:50 in a 02:00–04:00 window → stop and roll back per the plan | ITIL 4 Change enablement (implementation within the authorised window, remediation plan) | Correct |
| 37 | S-IT-12.2.2 (IT-12.2) | exam_supplement | Personal data only for job need; never share a login | NIST SP 800-53 Rev. 5 AC-6 (least privilege), IA-2/IA-5 (individual authenticators) | Correct |
| 38 | X-IT-12.3.3 (IT-12.3) | EXPANSION | Nightly backups cannot meet a one-hour RPO | NIST SP 800-34 Rev. 1 (recovery point objective) | Correct |
| 39 | Q12.11 (IT-12.4) | ITSUP checks | Device moves to spares → status and location change, tag and serial stay | ITIL 4 IT asset management practice (asset lifecycle states); course 12.4 | Correct |
| 40 | X-IT-13.1.2 (IT-13.1) | EXPANSION | 169.254 + blank gateway → no DHCP answer; no link shows "Media disconnected" | IETF RFC 3927 (IPv4 link-local); Microsoft Learn, ipconfig | Correct |
| 41 | X-IT-13.2.2 (IT-13.2) | EXPANSION | nslookup right, browser wrong → hosts file and DNS client cache | Microsoft Learn, nslookup (queries the DNS server directly) and DNS client resolver cache / hosts file | Correct |
| 42 | Q13.6 (IT-13.3) | ITSUP checks | Settings-paths gym: About, Ethernet, Update, Accounts, Services | Course lesson 13.5 lab list (course procedure) | Correct |
| 43 | Q13.10 (IT-13.4) | ITSUP checks | 169.254 after a cable move → renew the lease first (lowest rung) | Course 13.4 reset ladder; Microsoft Learn, ipconfig /release and /renew | Correct |
| 44 | N1.7 (NO-1.2) | question_bank.N1 | /64 is the common IPv6 host subnet | IETF RFC 4291 section 2.5.1; RFC 7421 (64-bit boundary) | Correct |
| 45 | NQ2.1 (NO-2.1) | NETOPS checks | Patch cable between two jacks → layer-2 loop, broadcast storm | IEEE 802.1Q (spanning tree); Cisco STP configuration guide, PortFast and BPDU Guard | Correct. SME note (rationale wording on STP) |
| 46 | NQ2.3 (NO-2.2) | NETOPS checks | One VLAN fails across a working trunk → check the allowed VLAN list | IEEE 802.1Q; Cisco IOS, switchport trunk allowed vlan / show interfaces trunk | Correct |
| 47 | NQ2.7 (NO-2.3) | NETOPS checks | Toner and probe trace a jack to its patch-panel port without a live network | Cable-tester vendor documentation (tone generator and inductive probe, no active network needed) | Correct |
| 48 | N1.18 (NO-3.1) | question_bank.N1 | Anycast: several sites advertise one address, clients reach the nearest | IETF RFC 4786 (Operation of Anycast Services) | Correct |
| 49 | NQ3.3 (NO-3.2) | NETOPS checks | Before calling the provider: timestamps, interface errors, test results | Course lesson for NO-3.2 (provider escalation evidence); CompTIA Network+ N10-009 objective 5.1 (document findings) | Correct |
| 50 | NQ3.5 (NO-3.3) | NETOPS checks | Non-overlapping 2.4 GHz channels in 20 MHz: 1, 6, 11 | IEEE 802.11-2020, 2.4 GHz channel plan (5 MHz channel spacing, 20/22 MHz channel width) | Correct |
| 51 | NQ4.1 (NO-4.1) | NETOPS checks | New VLAN gets 169.254, DHCP server elsewhere → missing relay (helper) | IETF RFC 2131; RFC 1542 (relay agents) | Correct |
| 52 | NQ4.4 (NO-4.2) | NETOPS checks | Old IP still reached → cached records within TTL | IETF RFC 1035 (TTL); RFC 2308 (caching) | Correct |
| 53 | N1.8 (NO-4.3) | question_bank.N1 | Many-to-one NAT: inbound needs explicit port mappings | IETF RFC 3022 (NAPT); RFC 4787 | Correct |
| 54 | N2.15 (NO-5.1) | question_bank.N2 | Low latency, high jitter → voice degrades | IETF RFC 3550 section 6.4.1 (interarrival jitter) | Correct |
| 55 | N2.10 (NO-5.2) | question_bank.N2 | Management plane: AAA, SSH/HTTPS, management ACLs, logging | IETF RFC 6192 (protecting the router control plane); NIST SP 800-53 AC-17, AU-2 | Correct |
| 56 | N2.13 (NO-5.3) | question_bank.N2 | Overlay segmentation (VXLAN) scales beyond VLANs | IETF RFC 7348 (VXLAN, 24-bit VNI) | Correct |
| 57 | NQ6.1 (NO-6.1) | NETOPS checks | One user, one site failing → the user’s device or account | CompTIA Network+ N10-009 objective 5.1 (identify scope); course lesson for NO-6.1 | Correct |
| 58 | NQ6.4 (NO-6.2) | NETOPS checks | A good change plan already contains a tested rollback | ITIL 4 Change enablement (remediation/backout plans); NIST SP 800-128 | Correct |
| 59 | S-NO-6.3.2 (NO-6.3) | exam_supplement | Trunk VLAN change → update the network diagram and configuration record | NIST SP 800-128 (configuration baselines and change records); course lesson for NO-6.3 | Correct |
| 60 | NQ9.1 (NO-9.1) | NETOPS checks | Access port in VLAN 20: switchport mode access, switchport access vlan 20 | Cisco IOS LAN Switching configuration guide, access ports | Correct |
