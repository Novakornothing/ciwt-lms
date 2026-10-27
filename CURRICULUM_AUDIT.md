# Curriculum audit — pass 8 (October 2026)

Scope: IT Support Fundamentals (ITSUP, 13 chapters, 59 lessons), Network Operations (NETOPS, chapters 1–6 and 9,
30 lessons), Client Systems Support (CLIENT = ITSUP chapters 8–13), 46 interactive labs, knowledge-test banks
(A1–A3, N1–N3: 140 items → six 50-item forms), 130 ITSUP chapter-check items, NETOPS chapter checks and skills exams.
Method: `tools/curriculum_inventory.py` (structure, word counts, reading level, objective verbs, accessibility
signals, item heuristics), then a read-through of every lesson and every assessment item. Factual claims were
checked against the sources listed at the end. Stance kept: **original curriculum, not a vendor exam product**;
no vendor affiliation is claimed and no vendor exam items are used.

All originals stay recoverable: the revised content is a layer (`curriculum_v2/`) applied on top of
`lessons.py`, `question_bank.py` and `pilot_slice.py`, whose text is unchanged in place and in git.

## Headline findings

1. **NETOPS chapter checks were not chapter checks.** The seeder rotated three generic 10-item sets across the
   seven chapters (chapters 4 and 9 repeated chapter 1; 5 repeated 2; 6 repeated 3). Items were off-chapter and used
   joke distractors ("Generate thermal paste", "Only the office coffee stock"). → Replaced with 56 chapter-specific
   items (8 per chapter), each mapped to an objective with a rationale (`curriculum_v2/netops_checks.py`).
2. **Two knowledge-test items were wrong.** N1.2 had two correct answers (192.168.10.255 is a valid host in
   192.168.10.0/23). N1.4's key hedged ("before or after routing depending on design"); an inbound ACL is evaluated
   as the packet enters, before the routing decision. A1.13's stem gave the answer away ("/27").
3. **The answer was guessable by length.** Before review the key was the longest option in 200 of 300 test items and
   80 of 130 chapter-check items; in 120 of 269 unique items it was over 1.6× the longest distractor. After the parity
   pass: 8 items over 1.6×, 2 over 2.0× (test-enforced ≤ 2 %). Chapter-check keys sat in position B in 85 of 130
   items; now 32–33 per position.
4. **No item had a rationale, and none was mapped to a measurable objective.** All 270 bank/check items (+56 NETOPS
   checks, +30 supplementary items) now carry an objective code and an instructor rationale.
5. **NETOPS lessons were mostly boilerplate.** Chapters 2–6 were about 75 % templated text (only 390–600 unique words
   per chapter for about 6 hours of seat time) with one-word objective fragments. → 18 core-content sections
   (~6,900 words) and 110 measurable objectives added (`curriculum_v2/netops_core.py`). NETOPS words 11,985 → 18,892.
6. **ITSUP chapters 7–13 are thin** (about 800–1,000 words for about 3 hours each) and wireless was nearly absent.
   Reference sections were added (DDR4/DDR5, storage interfaces, USB/Thunderbolt/display naming, ports, Wi-Fi 4–7
   and SOHO baseline, Windows 11 requirements/lifecycle, Linux commands, MFA/passkeys/NIST 800-63B-4). Chapters
   7–13 still needed expansion after pass 8. → **Pass 9:** chapters 7–13 expanded to 3,355–4,643 words each (see
   “Pass 9” below); the new content is tagged *Pending SME review*. **Pass 10:** chapters 3–6 expanded the same way
   (2,475–3,399 core words added; 4,250–6,222 words of page text each).
7. **Assessment coverage gaps.** 12 ITSUP and 3 NETOPS objectives had no knowledge-test item. → 30 supplementary exam
   items (`curriculum_v2/exam_supplement.py`); every objective now has ≥ 2 items (test-enforced). The CLI-track
   objectives (ITSUP 13, NETOPS 9) are assessed practically in the skills exams and marked so in the blueprints.
8. **Labs:** ITSUP chapters 4, 6, 7, 9, 11, 12 and NETOPS 5 had no lab; three labs were unused (rtr-trace,
   win-getmac, win-netstat). → Unused labs mapped; existing labs attached to ITSUP 7/11 and NETOPS 5; four classroom
   labs written (CL-4 print path/FRU, CL-6 VM build/snapshot, CL-9 Linux CLI, CL-12 change request/recovery). No
   broken lab references.
9. **Teaching notes were shown to students** (an `.instructor-note` block in all 59 ITSUP lessons). → Now shown to
   staff only.
10. **Answer keys were visible in page source** on quiz/test pages (full question JSON incl. `correct`). → Fixed
    earlier in this pass (`public_questions` filter, tests).
11. **Outdated technical content:** a Windows 11 23H2 example and lab VM (Education/Enterprise 23H2 ends
    10 Nov 2026) → 25H2; lab VM setup referenced VMware Player (discontinued) and no virtual TPM → updated.

## Coverage map (after pass 9)

| Course | Ch | LMS min | Lesson objectives | Interactive labs | Classroom lab | Check items | Test + suppl. items |
|---|---|---|---|---|---|---|---|
| ITSUP | 1 Foundations & safety | 435 | 4 | 1 | — | 10 | yes |
| ITSUP | 2 Motherboard, CPU, memory | 360 | 4 | 1 | — | 10 | yes |
| ITSUP | 3 Storage, power, ports | 260 | 4 | 2 | — | 10 | yes |
| ITSUP | 4 Mobile & printing | 205 | 3 | 0 | CL-4 | 10 | yes |
| ITSUP | 5 Client networking | 280 | 4 | 14 | — | 10 | yes |
| ITSUP | 6 Virtualisation & cloud | 185 | 3 | 0 | CL-6 | 10 | yes (suppl.) |
| ITSUP | 7 Troubleshooting method | 185 | 4 | 2 | CL-7 | 10 | yes (suppl.) |
| ITSUP | 8 Windows install & config | 195 | 4 | 8 | CL-8 | 10 | yes |
| ITSUP | 9 Linux, macOS | 175 | 4 | 0 | CL-9 | 10 | yes |
| ITSUP | 10 Endpoint security | 180 | 4 | 3 | CL-10 | 10 | yes |
| ITSUP | 11 Software troubleshooting | 185 | 4 | 2 | CL-11 | 10 | yes (suppl.) |
| ITSUP | 12 Operational procedures | 175 | 4 | 0 | CL-12 | 10 | yes |
| ITSUP | 13 Windows CLI & VM track | 230 | 4 | 16 | CL-13 | 10 | skills exam |
| NETOPS | 1 Models & addressing | 360 | 3 | 3 | — | 8 | yes |
| NETOPS | 2 Switching, VLANs, cabling | 360 | 3 | 9 | — | 8 | yes |
| NETOPS | 3 Routing, WAN, wireless | 355 | 3 | 6 | — | 8 | yes |
| NETOPS | 4 DHCP, DNS, NAT, firewall | 385 | 3 | 2 | — | 8 | yes |
| NETOPS | 5 Monitoring, hardening | 355 | 3 | 3 | — | 8 | yes |
| NETOPS | 6 Troubleshooting capstone | 360 | 3 | 3 | — | 8 | yes (suppl.) |
| NETOPS | 9 Switch & router CLI | 480 | 2 | 8 | — | 8 | suppl. + skills exam |

Totals: ITSUP ≈ 3,050 LMS minutes (≈ 51 h), NETOPS ≈ 2,655 (≈ 44 h), CLIENT ≈ 1,140 (≈ 19 h). These are
content-author estimates of guided study and lab time, not measured student time. A 4-credit (3 lecture + 1 lab)
semester gives 75 contact hours + ~90 out-of-class hours (34 CFR 600.2), which accommodates this content plus
assessments; see the pacing guides.

## Objective quality

- 50 ITSUP (5 added in pass 9: IT-7.4, 9.4, 11.4, 12.4, 13.4) and 20 NETOPS chapter-level objectives with Bloom levels (`curriculum_v2/objectives.py`), grouped under
  6 course learning outcomes per course (5 for CLIENT); every objective maps to a CLO (test-enforced).
- 7 vague ITSUP lesson objectives ("Know…") rewritten with measurable verbs (1.2, 1.4, 2.2, 3.2, 6.1, 6.2, 6.3).
- NETOPS lesson objectives were one-word fragments; now 3–4 measurable objectives per lesson.

## Assessment review (all items)

- 270 bank and chapter-check items reviewed: 226 revised, 44 kept as written. 226 got new same-domain distractors,
  173 keys were tightened, 21 stems rewritten (fragments without a question, stem clues, ambiguity), 2 incorrect items
  fixed. Joke/cross-domain distractors ("Yes if it is Tuesday", "A RAID level", "Vendor-specific distractor") replaced.
- Every entry is keyed by bank position with a stem guard: if a bank is reordered, a test fails rather than applying a
  revision to the wrong item (`curriculum_v2/item_review.py`).
- Blueprints: midterm (ITSUP ch 1–7, NETOPS ch 1–4 + 9, CLIENT ch 1–3) and cumulative final, items per objective with
  Bloom mix and item IDs. The LMS Tests A–C are cumulative forms; the blueprints show how each form spreads across
  chapters (e.g. ITSUP Test A has no chapter 6 or 13 items and 11 chapter 10 items).
- Note: past attempts keep their stored scores; item analysis of attempts taken before the revision compares old
  answers to revised keys.

## Factual corrections and updates (verified)

| Topic | Was | Now |
|---|---|---|
| Windows 11 release in examples and lab VM | 23H2 | 25H2, build 26200.x (23H2 Education/Enterprise service ends 10 Nov 2026) |
| Windows 10 | treated as current | end of support 14 Oct 2025; ESU through 12 Oct 2027 noted |
| VM setup | VMware Player; no TPM | Workstation Pro (free since Nov 2024; Player discontinued), Hyper-V, VirtualBox 7+; Windows 11 guest needs UEFI + Secure Boot + vTPM 2.0, 4 GB RAM, 64 GB |
| Passwords | composition rules + periodic change implied | NIST SP 800-63B-4: length (15 single-factor, 8 with MFA), breached-list screening, no composition rules, no forced periodic change |
| Wireless | one WPA line | Wi-Fi 4–7 generations, 6 GHz requires WPA3, channel plans, SNR |
| USB/Thunderbolt/display | — | USB-IF naming (USB 5/10/20/40/80 Gbps), USB PD up to 240 W, HDMI 2.1 48 Gb/s, DP 2.1 80 Gb/s, Thunderbolt 5 |
| Memory | — | DDR4 vs DDR5 (not slot-compatible, on-module PMIC, two subchannels) |
| N1.2 / N1.4 | wrong items | corrected (see above) |
| 10GBASE-T on Cat6 | — | ~55 m limit stated (Cat6A for 100 m) |

## Accessibility

- Pass 9 added 8 inline SVG diagrams (ITSUP 7–13). Each has `role="img"` with a `<title>` and `<desc>` (the alt text),
  a caption and an expandable “Text description of the diagram”; a separate two-column version is shown on phones.
  Data tables all have header cells; no heading skips.
- Narration is synthesised from the on-page text, so the page is the transcript; there is no pre-recorded audio or
  video needing captions.
- Reading level (automated Flesch–Kincaid estimate): ITSUP ≈ grade 7.7, NETOPS ≈ 10.9 (technical terms raise it).
- New pages pass axe-core in light and dark themes (see REFINEMENT_NOTES.md). DOCX tables mark header rows.

## Still needs a subject-matter expert or the institution

- **SME:** review the pass-9 ITSUP 7–13 core content, 85 items and 5 classroom labs (all tagged *Pending SME review*);
  review all 30 supplementary items and 56 NETOPS checks; field-test
  item difficulty (p-values) and distractor performance after one cohort; confirm lesson minute estimates against real
  class timing; check classroom labs CL-4/6/7/8/9/10/11/12/13 on the institution's hardware; decide whether to publish chapter-limited
  midterm forms in the LMS (blueprints list the item IDs).
- **Institution:** catalog numbers, credit model (lab contact hours per credit), prerequisites, all policy text
  (attendance, late work, academic integrity, AI use, accessibility office, non-discrimination, appeals), Windows and
  virtualisation licensing for labs, and any articulation or accreditation claims (none are made here).
- **Alignment:** if the program wants a mapping to a publicly published vendor exam objective list, do it as a
  labelled alignment table against the current published version; no such mapping is included.

## Pass 9 (Oct 17 2026): ITSUP chapters 7–13 expanded — pending SME review

Layered in `curriculum_v2/itsup_core/` (one module per chapter). The original lesson HTML is unchanged in `lessons.py`
and git. Each lesson gets a “Lesson objectives” panel and a `Core content` section with a sources line. CLIENT
chapters 1–6 inherit ITSUP 8–13. An instructor-only “Pending SME review” note sits in every expanded lesson; students
don't see it. The tag is also on lesson plans, labs, the answer-key bank and glossary terms (†).

| Ch | Words before → after | Added | Items | Lab |
|---|---|---|---|---|
| 7 | ~1,230 → 4,242 | method comparison, 7-step cycle diagram, “Outlook won't send” worked example, printer scenario, fault domains, escalation evidence package (new IT-7.4), capstone drills | 12 | CL-7 staged-fault drills (new) |
| 8 | ~1,100 → 4,643 | install options, Win 11 requirements and servicing, Win 10 end of support, baseline, LAPS, GPO order and refresh, Kerberos skew and trust failure, DISM → SFC, WinRE, Quick machine recovery, failed-update capstone | 13 | CL-8 recovery ladder (new) |
| 9 | ~900 → 3,874 | Linux commands, permissions diagram, systemd/journalctl, nginx worked example, macOS recovery, FileVault, Time Machine, MDM/Activation Lock, file-system table, SMB/SSH (new IT-9.4) | 12 | CL-9 (existing) |
| 10 | ~800 → 3,856 | phishing resistance of MFA types, MFA-fatigue scenario, malware isolate/preserve/report, Defender Offline, BitLocker recovery, NIST 800-88r2 sanitisation, mailbox-rule follow-up, RFC 3227 order of volatility, chain of custody | 12 | CL-10 posture check + tabletop (new) |
| 11 | ~480 → 3,355 | fault shapes (Event IDs 1000/1002), scoping diagram, clean boot with halving, Safe Mode, repair/reset table, repair-vs-rebuild time boxes, slow-logon stages, Resource Monitor, temporary profiles (new IT-11.4) | 12 | CL-11 slow PC (new) |
| 12 | ~680 → 3,532 | change types and change request, lifecycle diagram, PII and minimum access, AUP/licensing/BYOD, 3-2-1, full/incremental/differential, RPO/RTO, KB article/runbook/asset record (new IT-12.4), integrated capstone | 12 | CL-12 (existing) |
| 13 | ~1,130 → 4,178 | VM snapshot loop diagram, baseline inventory, safe vs destructive commands, ipconfig /all and APIPA, WMIC → CIM/NetTCPIP/DnsClient table, network-reset ladder, desk-move scenario, IP-vs-name diagram, hosts/cache/server comparison, Settings ↔ command map, tasklist /svc, netsh, restart decisions (new IT-13.4) | 12 | CL-13 PowerShell evidence + name-resolution repair (new) |

Word counts are visible lesson text after the layer is applied, excluding diagrams and styles. For comparison,
ch1 is 6,524 and ch2 is 3,493.

**Each lesson has:**
- 3–5 measurable objectives
- at least 300 words of core content
- 2–3 check-for-understanding questions with answers (`<details>`)

**Each chapter has:**
- a worked example
- a real-world troubleshooting scenario
- a described diagram
- glossary terms (64 in total)
- lesson-plan additions: warm-up, guided practice, worked examples, CFU questions, exit ticket, misconceptions, lab
- tests that enforce all of the above (`tests/test_itsup_expansion.py`)

**Items:**
- 85 new items (bank `X-IT-*`) across 28 objectives, at least 3 per objective, each with a rationale.
- Key positions are 22/21/21/21. The key is the longest option (including ties) in 22 of 85 items. The longest/shortest option ratio is ≤ 1.5 for every item.
- No "all/none of the above", and no vendor exam items. Every item was written from the lesson text.
- The items are in the answer key as “Chapter item bank, pass 9 — Pending SME review” and in the blueprints. Like the supplement, they are not on the live LMS Test A/B/C forms.

**Facts checked against current sources** (Microsoft Learn/Support, Apple Support, NIST, CISA, IETF, man pages):

| Topic | What the lesson says |
|---|---|
| WMIC | Removed from Windows 11 24H2/25H2 with the August 2026 update; no longer a Feature on Demand → `Get-CimInstance` |
| Windows 11 servicing | Home/Pro 24 months, Enterprise/Education 36 months; Windows 10 end of support 14 Oct 2025 |
| Repair order | DISM /RestoreHealth before `sfc /scannow` (Microsoft's documented order) |
| Recovery | “Fix problems using Windows Update” keeps apps/files/settings; go back within 10 days; Quick machine recovery present in current Windows 11 |
| Group Policy | Processing order local → site → domain → OU; background refresh 90 min + random 0–30 min |
| Kerberos | Default maximum clock skew 5 minutes |
| BitLocker | Device encryption on automatically with a Microsoft or work account; key at aka.ms/myrecoverykey |
| macOS Recovery | Apple silicon: press and hold the power button; Intel: Command-R |
| Sanitisation | NIST SP 800-88 Rev. 2 (final Sep 2025): clear / purge / destroy; cryptographic erase as a purge method |
| Incident response | NIST SP 800-61 Rev. 3 (Apr 2025) is organised under CSF 2.0; order of volatility from RFC 3227 |
| Backup | CISA 3-2-1 guidance |
| Name resolution | `Resolve-DnsName` -DnsOnly / -NoHostsFile / -Server; `Test-NetConnection -Port`; nslookup does not use the hosts file |
| Network reset | Settings → Network & internet → Advanced network settings → Network reset reinstalls adapters and restarts the PC |

macOS version names, market-share figures and incident statistics were left out on purpose. None could be checked
reliably, and no statistics or citations were invented.

**Still for the SME:**
- Accuracy and tone of all pass-9 text.
- Whether 3,300–4,600 words fits the 175–230 LMS minutes per chapter.
- Item difficulty after a cohort.
- CL-7/8/10/11/13 on real hardware.
- Whether to add any `X-IT` items to the live forms.

ITSUP chapters 3–6 (1,393–2,500 words) are the next thinnest. They were not in scope for this pass. → **Pass 10:** expanded (see below).

## Pass 10 (Oct 17 2026): ITSUP chapters 3–6 expanded — pending SME review

Same standard and the same layer (`curriculum_v2/itsup_core/ch03.py` … `ch06.py`, applied by `curriculum_v2.apply`;
the original lesson text is unchanged). Everything is tagged *Pending SME review*.

| Chapter | Words now (page text, as the tests count it) | Core words added | Figures | Items | Glossary |
|---|---|---|---|---|---|
| 3 Storage, power, ports | 6,222 | 3,258 | f3-2 RAID vs backup, f3-4 display isolation | 14 (IT-3.1–3.4) | 13 |
| 4 Mobile devices & printing | 5,258 | 3,399 | f4-2 retire/wipe decision, f4-3 print path | 10 (IT-4.1–4.3) | 14 |
| 5 Networking for support | 5,626 | 3,044 | f5-2 DHCP DORA, f5-3 isolation order | 13 (IT-5.1–5.4) | 14 |
| 6 Virtualization & cloud | 4,250 | 2,475 | f6-2 SaaS provider-or-local, f6-3 checkpoint chain | 9 (IT-6.1–6.3) | 14 |

Per lesson: 3–5 measurable objectives, core explanation, ≥1 worked example or scenario per chapter (most lessons have one),
check-for-understanding questions with hidden answers, and sources. Per chapter: a lesson-plan update (warm-up, guided
practice, CFU, exit ticket, misconceptions, materials) and items (≥2 per objective, distractor lengths balanced, key
positions balanced across the whole bank, rationale for each).

**Facts checked against named sources** (keys in `itsup_core.SOURCES`): NVMe specification; Microsoft storage, display, print
(Print Spooler, protected print mode) and Hyper-V documentation (requirements, switch types, standard/production checkpoints);
PCI-SIG CEM; USB-IF naming and USB PD (100 W SPR, 240 W EPR); CISA backup, ransomware and home-wireless guidance; U.S. EPA
used lithium-ion batteries; Microsoft Intune retire/wipe and compliance; Apple Platform Deployment (Activation Lock, private
Wi-Fi address); IETF RFC 8011 (IPP), RFC 1918, 3927, 6598, 4291, 4193, 4862, 2131 (T1 50 %, T2 87.5 %), RFC 6335/IANA ports;
netsh wlan; NIST SP 800-145 and 800-125; Microsoft shared responsibility and Microsoft 365 Service health.

**For the SME:** the Hyper-V Paused-Critical wording avoids a free-space threshold on purpose; the 2.4 GHz “1, 6, 11” rule is
stated for North America; printer defect causes are typical, and the vendor’s defect guide is authoritative. Chapter 3 and
4 items were committed with ch03 (8062cbd) and ch04–06 in one commit (8e0ff0d).

**Lab gaps (for the labs worker; no lab formats were changed):**
- 4.1: no lab for `powercfg /batteryreport` (a VM has no battery, so this needs a physical laptop or a canned report).
- 4.3: no hands-on spooler lab (stop Print Spooler, clear `spool\PRINTERS`, start, test page — could use a Print-to-PDF queue); CL-4 is paper-based.
- 5.1–5.2: no interactive subnet drill or `Test-NetConnection -Port` / `nslookup -type=MX` lab; the existing win-ipconfig / win-dns-break / win-full-triage labs cover 5.3 and 5.5.
- 5.4: w11-wlan needs a wireless adapter; on VM benches `netsh wlan show interfaces` reports no interface.
- 6.1: the “Virtual machine: Yes” / systeminfo check could be added to w11-inventory or gui-about.
- 6.3: virtual switch and checkpoint practice needs a Hyper-V host or nested virtualization; CL-6 covers it on classroom hardware only.

## Sources consulted

Microsoft Learn — Windows 11 release information and lifecycle; Microsoft Support — Windows 10 end of support and ESU;
Microsoft — Windows 11 specifications and system requirements; NIST SP 800-63B-4 (July 2025); IEEE 802.11ax/be and
Wi-Fi Alliance requirements as summarised in vendor design guides; USB-IF Data Performance Language Usage Guidelines
(Jan 2024); Intel Thunderbolt 5 brief; JEDEC DDR5 (JESD79-5 family); PCI-SIG base specifications; IANA port registry;
Broadcom/VMware Workstation Pro licensing announcement (Nov 2024); 34 CFR 600.2 credit-hour definition (eCFR, version
dated 1 Jul 2026). Pass 9: Microsoft Learn (Windows commands; NetTCPIP, DnsClient and CimCmdlets modules; System File
Checker; Windows recovery options; Group Policy processing; Kerberos policy; Windows lifecycle), Microsoft Support
(WMIC removal; BitLocker/device encryption; Microsoft Defender Offline; network reset), Apple Support (macOS Recovery,
FileVault, Time Machine), NIST SP 800-88r2, 800-61r3, 800-63B-4, IETF RFC 3227, CISA backup and MFA guidance, Linux
man-pages and systemd documentation.
