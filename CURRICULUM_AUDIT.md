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
   7–13 still need SME expansion (see below).
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

## Coverage map (after pass 8)

| Course | Ch | LMS min | Lesson objectives | Interactive labs | Classroom lab | Check items | Test + suppl. items |
|---|---|---|---|---|---|---|---|
| ITSUP | 1 Foundations & safety | 435 | 4 | 1 | — | 10 | yes |
| ITSUP | 2 Motherboard, CPU, memory | 360 | 4 | 1 | — | 10 | yes |
| ITSUP | 3 Storage, power, ports | 260 | 4 | 2 | — | 10 | yes |
| ITSUP | 4 Mobile & printing | 205 | 3 | 0 | CL-4 | 10 | yes |
| ITSUP | 5 Client networking | 280 | 4 | 14 | — | 10 | yes |
| ITSUP | 6 Virtualisation & cloud | 185 | 3 | 0 | CL-6 | 10 | yes (suppl.) |
| ITSUP | 7 Troubleshooting method | 185 | 3 | 2 | — | 10 | yes (suppl.) |
| ITSUP | 8 Windows install & config | 195 | 4 | 8 | — | 10 | yes |
| ITSUP | 9 Linux, macOS | 175 | 3 | 0 | CL-9 | 10 | yes |
| ITSUP | 10 Endpoint security | 180 | 4 | 3 | — | 10 | yes |
| ITSUP | 11 Software troubleshooting | 185 | 3 | 2 | — | 10 | yes (suppl.) |
| ITSUP | 12 Operational procedures | 175 | 3 | 0 | CL-12 | 10 | yes |
| ITSUP | 13 Windows CLI & VM track | 230 | 3 | 16 | — | 10 | skills exam |
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

- 45 ITSUP and 20 NETOPS chapter-level objectives with Bloom levels (`curriculum_v2/objectives.py`), grouped under
  6 course learning outcomes per course (5 for CLIENT); every objective maps to a CLO (test-enforced).
- 7 vague ITSUP lesson objectives ("Know…") rewritten with measurable verbs (1.2, 1.4, 2.2, 3.2, 6.1, 6.2, 6.3).
- NETOPS lesson objectives were one-word fragments; now 3–4 measurable objectives per lesson.

## Assessment review (all items)

- 270 bank and chapter-check items reviewed: 226 revised, 44 kept as written. 226 got new same-domain distractors,
  173 keys were tightened, 21 stems rewritten (fragments without a question, stem clues, ambiguity), 2 incorrect items
  fixed. Joke/cross-domain distractors ("Yes if it is Tuesday", "A RAID level", "Official CompTIA") replaced.
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

- Lesson bodies contain no images (nothing needs alt text); 123 data tables, all with header cells; no heading skips.
- Narration is synthesised from the on-page text, so the page is the transcript; there is no pre-recorded audio or
  video needing captions.
- Reading level (automated Flesch–Kincaid estimate): ITSUP ≈ grade 7.7, NETOPS ≈ 10.9 (technical terms raise it).
- New pages pass axe-core in light and dark themes (see REFINEMENT_NOTES.md). DOCX tables mark header rows.

## Still needs a subject-matter expert or the institution

- **SME:** expand ITSUP chapters 7–13 lesson text; review all 30 supplementary items and 56 NETOPS checks; field-test
  item difficulty (p-values) and distractor performance after one cohort; confirm lesson minute estimates against real
  class timing; check classroom labs CL-4/6/9/12 on the institution's hardware; decide whether to publish chapter-limited
  midterm forms in the LMS (blueprints list the item IDs).
- **Institution:** catalog numbers, credit model (lab contact hours per credit), prerequisites, all policy text
  (attendance, late work, academic integrity, AI use, accessibility office, non-discrimination, appeals), Windows and
  virtualisation licensing for labs, and any articulation or accreditation claims (none are made here).
- **Alignment:** if the program wants a mapping to a publicly published vendor exam objective list, do it as a
  labelled alignment table against the current published version; no such mapping is included.

## Sources consulted

Microsoft Learn — Windows 11 release information and lifecycle; Microsoft Support — Windows 10 end of support and ESU;
Microsoft — Windows 11 specifications and system requirements; NIST SP 800-63B-4 (July 2025); IEEE 802.11ax/be and
Wi-Fi Alliance requirements as summarised in vendor design guides; USB-IF Data Performance Language Usage Guidelines
(Jan 2024); Intel Thunderbolt 5 brief; JEDEC DDR5 (JESD79-5 family); PCI-SIG base specifications; IANA port registry;
Broadcom/VMware Workstation Pro licensing announcement (Nov 2024); 34 CFR 600.2 credit-hour definition (eCFR, version
dated 1 Jul 2026).
