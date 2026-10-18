# Curriculum readiness — ITSUP and NETOPS (pass 13, 18 Oct 2026; updated passes 14 and 15)

> **Pass 15 update.**
>
> - **Short rationales.** The 41 short ITSUP/CLIENT rationales are now full explanations. They come from 39 ITSUP bank items; Q8.6 and Q8.8 are also served in CLIENT, which makes 41. Each says why the key is right and why the main distractor is wrong, and keeps the section pointer. They are in `curriculum_v2/rationales_pass15.py`. Keys are unchanged. No chapter-check rationale is now under 10 words. *Pending SME review.*
> - **Longest-option giveaway.** Before this pass, the key was the uniquely longest option in 108 of the 200 ITSUP and NETOPS chapter-check items (54%). Options were rebalanced in about 88 items (`curriculum_v2/parity_pass15.py`). Distractors were lengthened with plausible detail that keeps the same wrong idea, and a few keys were tightened. Meaning and keys are unchanged, and misconception tags moved with the rewritten text. The pass-14 items Q12.11 and Q13.11 are no longer giveaways.
>   - The key is now uniquely longest in 31 of 200 (about 16%), below the roughly 25% expected by chance with four options.
>   - Only NQ1.5 (HTTPS) and NQ4.5 (CNAME) still have a key more than 15% longer than every distractor. Both are one-term answers, so shortening them further would change the wording of the concept.
> - **Audit.** Two new checks: every chapter-check rationale has at least 10 words, and the share of items whose key is uniquely longest is reported. That check passes at 30% or less, with at most max(2, n/50) clear-margin items.
> - **Certification gaps closed.** 59 new certification items are in `curriculum_v2/cert/content/i05_gaps_p15.py`:
>   - two or three for each of the 22 objectives that had none (ITSUP: IT-1.1, 1.3, 2.4, 5.1, 7.1–7.4, 8.3, 8.4, 11.2, 11.4, 12.3, 12.4, 13.3; NETOPS: NO-1.2, 1.3, 2.2, 3.1, 4.1, 4.2, 6.2);
>   - one more each for IT-2.2, IT-6.3, IT-13.1 and NO-9.2, which had only one.
>
>   Every ITSUP and NETOPS objective now has at least two certification items, and A1, A2 and N+ objectives are all 100% covered (see `CERT_COVERAGE.md`). Each new item is tied to a curated official exam objective, lists a primary source (RFC, IEEE, IANA, Microsoft, Cisco or CompTIA objectives) in `SOURCE`, and carries misconception tags (47 new misconceptions). All are *Pending SME review*. Grok Bot wrote and checked them; an SME has not.
> - The pass 14 text below is kept as written; SME list items 1, 2 and 5 are updated.

> **Pass 14 update.**
>
> - **New chapter-check items.** IT-7.4, 8.4, 9.4, 10.4, 11.4, 12.4 and 13.4 now have chapter-check items: two each, 14 in all, in `curriculum_v2/checks_pass14.py`. They are appended to each chapter check, so existing item positions, bank ids and stored attempts are unchanged.
>   - Each item has a full rationale and a primary source, listed per item in `SOURCE`.
>   - Each item carries misconception tags: 14 misconceptions, 37 tags.
>   - All 14 are labelled *Pending SME review*, and the instructor answer key shows that label.
> - **Rationales.** The 64 ITSUP chapter-check items whose rationale was only a section reference (the earlier count of 62 used a stricter rule) now have full explanations, in `curriculum_v2/rationales_pass14.py`. Keys and options are unchanged and the section pointer is kept. These rationales are also pending SME review.
> - **Audit.** The audit now has 28 checks, all passing. The three new checks are: ITSUP and NETOPS objectives each have chapter-check items, and every chapter-check rationale explains its answer. Output is in `docs/readiness/readiness-pass14.json`.
> - **Accuracy spot-check round 2.** 60 more original items were checked, one per objective, covering every chapter. The list is in `docs/readiness/SPOT_CHECK_ROUND2.md`. **No answer key was wrong.** Fixes: 4 stems clarified (A2.17, N1.20, NQ1.1, NQ4.5) and 4 rationales made precise (X-IT-3.1.1, X-IT-13.2.1, N1.20, NQ4.5), all *Pending SME review*. Still open: 61 of the 144 ITSUP chapter-check items have a one-line rationale under 90 characters that starts with a section pointer, for example Q1.5 "1.2 / 1.5 — heat and shock are not solo swaps." The audit accepts these because they are not pointer-only, but they are thin.
> - **Accuracy spot-check round 3 (content round 3).** 60 more original items, none from rounds 1–2, least-checked objectives first (`docs/readiness/SPOT_CHECK_ROUND3.md`, frozen list `docs/readiness/spot-check-round3-sample.json`). **No answer key was wrong; no key changed.** One stem clarified (X-IT-9.2.3: the Mac is college-owned), *Pending SME review*. 23 ITSUP chapter-check items still have a one-line rationale under 90 characters (listed there).
> - The pass 13 text below is kept as written, except that SME items 1 and 5 are updated.


**Bottom line.** The automated audit passes all 25 checks on a copy of the production database. The 40-item accuracy spot-check of the original course bank found no wrong answer keys. It led to one stem rewrite, one rationale correction, and one duplicate-stem fix. The audit also caught a real first-boot bug, which is now fixed. The content is ready to teach. The certification items and the passes 9–10 item bank still carry *Pending SME review* labels, and the list at the end says what an SME should look at first.

How to re-run (database copy only; the tool renders pages and logs in):

```bash
cp ciwt_lms.db /tmp/copy.db
./venv/bin/python tools/build_course_package.py /tmp/pkg                 # writes /tmp/pkg/MANIFEST.json
DATABASE_URL=sqlite:////tmp/copy.db ./venv/bin/python tools/curriculum_readiness.py out.json --package /tmp/pkg
```

The full output of this run is in `docs/readiness/readiness-pass13.json`, with per-objective rows and hours. `tests/test_curriculum_readiness.py` runs the same audit on the seeded test database in every `pytest` run.

## Checklist

| Area | Check | Result |
|---|---|---|
| Lessons | ITSUP: all 59 lessons render for staff and for an enrolled student. Each returns 200 with no `{{`, `{%`, `Traceback`, `undefined` or template-variable `None` | **PASS** |
| Lessons | NETOPS: all 30 lessons render (same test) | **PASS** |
| Lessons | Every lesson has at least 900 characters of prose | **PASS**, but see note 4 |
| Objectives | ITSUP (50) and NETOPS (20): every objective's chapter is in the LMS | **PASS** |
| Objectives | Every objective has at least one lesson, mapped by the engine from the objective text | **PASS** |
| Objectives | Every objective has original (non-certification) items | **PASS**. ITSUP minimum 3, NETOPS minimum 4 |
| Objectives | Every objective has a lab, either attached to a lesson or a chapter lab | **PASS** |
| Objectives | Every objective's lessons use at least one glossary term (173 terms) | **PASS** |
| Keys | Every original item (487) has a valid key: the key is one of the options, options are distinct, and there are at least 2 | **PASS** |
| Keys | Every certification item (415) has a valid key | **PASS** |
| Keys | Chapter-check answer keys in the package match what the LMS delivers: same items, same key, same option order | **PASS** |
| Keys | Knowledge-test items in the LMS are keyed | **PASS** |
| Items | No bank id is reused for different stems | **PASS** |
| Items | No identical stem under two bank ids | **PASS** after the fix (X-IT-9.2.2 duplicated S-IT-9.2.1) |
| Items | Every original item has an objective, and it is a current one | **PASS** |
| Items | No chapter check without a chapter | **PASS** |
| Documents | Lesson plans match the LMS: lesson titles in order, objectives, and minutes | **PASS** after the fix (NETOPS plan minutes, note 2) |
| Documents | The syllabus lists every chapter and states the computed contact hours (75 h per course; 34 CFR 600.2 basis) | **PASS** |
| Documents | Total LMS lesson time fits within contact plus out-of-class hours (ITSUP 50.8 h; NETOPS 38.2 h; budget 75 + 90 h) | **PASS** |
| Package | Regenerated from this tree; every document model hash matches `MANIFEST.json`; all files present | **PASS** |

## Fixes made in this pass

1. **First boot (bug, `app.py`).** `init_db()` returned right after seeding a brand-new database. Until the first restart, a new install therefore served the generic seed chapter checks. Those have no objective tags, so the adaptive engine had no check items, and the skills midterm and final were not synced either. The seed now runs the same content syncs as an existing database. A test now covers this (`test_a_brand_new_install_syncs_chapter_checks_on_first_boot`). Existing databases, including `ciwt_lms.db`, were never affected because they always run the syncs.
2. **Lesson-plan minutes (NETOPS).** The plan text says "About N minutes of LMS content". It was using the chapter totals in `lessons.py`, which are 50–75 minutes higher than the lesson times the LMS shows for NETOPS chapters 1–6 (and 60 minutes lower for chapter 9). Plans now use the sum of lesson minutes. The chapter totals in `lessons.py` are unchanged. An SME should decide whether those totals were meant to include the chapter check and labs (see below).
3. **Duplicate stem.** X-IT-9.2.2 (passes 9–10 bank) asked the same question as S-IT-9.2.1: "Which macOS tool is the closest match to Windows Task Manager?". X-IT-9.2.2 now asks which Activity Monitor tab shows per-app Energy Impact (key: Energy), checked against Apple's Activity Monitor guide. Same objective, same alignment, and still marked *Pending SME review*. Nothing in the database referenced the old wording.
4. **Spot-check fixes.** See below: the N2.8 stem and the X-IT-9.4.1 rationale.

## Accuracy spot-check: 40 original items

The sample is seeded and stratified, and contains no certification items. Re-draw it with `python tools/spot_check_sample.py 13`. The strata are:

| Source | Items |
|---|---|
| question_bank A1 | 6 |
| A2 | 4 |
| A3 | 3 |
| N1 | 5 |
| N2 | 4 |
| N3 | 3 |
| ITSUP chapter checks | 6 |
| NETOPS chapter checks | 4 |
| Exam supplement | 3 |
| Passes 9–10 bank | 2 |

Each item was checked against the primary source in the table. "Course" means the claim is a course rule; it was checked against the lesson that teaches it. The checking was done by Grok Bot, not by an SME.

| # | Item | Claim checked | Primary source | Verdict |
|---|---|---|---|---|
| 1 | A1.16 | Port 445 blocked → SMB shares fail | IANA service-name registry (microsoft-ds 445/tcp); MS-SMB2 | Correct |
| 2 | A1.18 | APIPA plus no switch link light → fix layer 1/2 before DHCP | RFC 3927 (169.254/16 link-local) | Correct |
| 3 | A1.43 | One external display from a dock → check dock bandwidth, cable and DP Alt Mode/MST | VESA DisplayPort Alt Mode on USB Type-C | Correct |
| 4 | A1.47 | Bind :443 without root → CAP_NET_BIND_SERVICE or a reverse proxy | Linux capabilities(7) man page | Correct |
| 5 | A1.11 | Mini-ITX: one expansion slot, 170 × 170 mm | Mini-ITX form-factor spec (VIA) | Correct |
| 6 | A1.41 | Delegate printer install instead of local admin | Microsoft least-privilege guidance (Point and Print / delegated install) | Correct |
| 7 | A2.7 | Promiscuous vNIC can capture other guests' traffic | VMware vSphere networking: promiscuous mode security policy | Correct |
| 8 | A2.4 | Captive portal allows DNS, blocks web until sign-in | RFC 8952 (captive portal architecture) | Correct |
| 9 | A2.19 | MDM blocks USB → exception process | Course 4.2 (policy) | Correct |
| 10 | A2.5 | Integrity → compare cryptographic hashes | NIST FIPS 180-4 (SHA-2); NIST SP 800-86 | Correct |
| 11 | A3.2 | /30 → 2 usable hosts | RFC 950 / RFC 1878 | Correct |
| 12 | A3.1 | RAID is not a backup | NIST SP 800-34 (backup vs redundancy) | Correct |
| 13 | A3.3 | TPM clear destroys Windows Hello for Business keys → re-enrol; BitLocker recovery | Microsoft Learn: WHfB how it works; BitLocker recovery | Correct |
| 14 | N1.23 | HSRP/VRRP = first-hop redundancy | RFC 5798 (VRRPv3); RFC 2281 (HSRP) | Correct |
| 15 | N1.9 | Enterprise per-user credentials → WPA2/3-Enterprise with 802.1X | IEEE 802.1X; Wi-Fi Alliance WPA3 spec | Correct |
| 16 | N1.0 | Per hop, routers rewrite L2 MACs and TTL; IPs stay the same without NAT | RFC 1812 §5.3.1, RFC 791 | Correct |
| 17 | N1.13 | TCP handshake SYN, SYN-ACK, ACK | RFC 9293 §3.5 | Correct |
| 18 | N1.4 | Inbound ACL is evaluated before the routing decision | Cisco IOS ACL configuration guide | Correct |
| 19 | N2.19 | Anycast → topologically nearest site | RFC 4786 | Correct |
| 20 | N2.0 | err-disabled after a host flaps → a protection feature (link-flap, BPDU Guard) | Cisco errdisable recovery documentation | Correct |
| 21 | N2.8 | Encrypted C2 → behavioural, flow and endpoint telemetry | NIST SP 800-94 | Key correct. **Stem fixed.** It read "detects encrypted C2 least by payload signatures alone", which is ambiguous and could be read as asking for the *worst* approach. Reworded in `curriculum_v2/item_review.py` |
| 22 | N2.4 | Tunnel mode protects the whole original packet | RFC 4301 §4.1 | Correct |
| 23 | N3.1 | Split-horizon DNS = different answers inside and outside | RFC 6950 §4 / common BIND views practice | Correct |
| 24 | N3.4 | Split tunnel excludes internal networks → route them through the tunnel | Vendor VPN split-tunnel docs (Microsoft Always On VPN routing) | Correct |
| 25 | N3.7 | OTDR locates fibre breaks and bad splices | ITU-T L.310 / TIA-568.3 OTDR testing | Correct |
| 26 | Q12.1 | Reseating RAM = a repair, still documented | Course 12.1 ("Reseat RAM = repair, still documented") | Correct. Rationale is only a section reference (note 1) |
| 27 | Q4.5 | Whole floor queued, panel says paper out → device first | Course 4.3 | Correct |
| 28 | Q7.5 | Ping to the internet works, tenant mail down → vendor/SaaS | Course 7.2 / 6.2 | Correct |
| 29 | Q10.1 | Taped shared admin password = unaccountable privilege | NIST SP 800-53 IA-2, AC-6 | Correct |
| 30 | Q6.9 | Don't delete a snapshot you don't own | Course 6.3/1.3 (snapshots are changes) | Correct |
| 31 | Q13.4 | Broken-name-resolution capstone labs = win-dns-break and win-full-triage | `interactive_labs.LABS` (both ids exist) | Correct. The distractor "hw-psu" is not a real lab id, which is acceptable as a distractor |
| 32 | NQ9.0 | `show vlan brief` lists access-port VLAN membership | Cisco Catalyst VLAN configuration guide | Correct |
| 33 | NQ5.3 | SNMPv3 adds authentication and privacy | RFC 3414 (USM) | Correct |
| 34 | NQ5.4 | SSH from the management subnet with AAA | NIST SP 800-53 AC-17; Cisco hardening guide | Correct |
| 35 | NQ4.3 | NXDOMAIN = the name does not exist | RFC 1035 §4.1.1 (RCODE 3), RFC 8020 | Correct |
| 36 | S-IT-11.2.2 | Rebuild → tested backup plus approved change | Course 11.2 / 12.1 | Correct |
| 37 | S-IT-7.1.2 | Theory disproved → new theory or escalate | Course 7.1 (published troubleshooting methodology) | Correct |
| 38 | S-NO-9.2.1 | Router-on-a-stick subinterface → `encapsulation dot1Q 20` | Cisco IOS inter-VLAN routing guide | Correct |
| 39 | X-IT-12.2.1 | Personal data sent by email → ask for the error text, delete the copy | Course 12.2; FERPA data-minimisation practice | Correct |
| 40 | X-IT-9.4.1 | exFAT for 6 GB files on Windows, macOS and Linux | Microsoft exFAT spec; Linux 5.7 fs/exfat (5.4 had only a staging driver) | Key correct. **Rationale fixed.** "Natively read/write on all three" now says "out of the box on current … Linux (in-kernel driver since Linux 5.7)" |

The tally is 40 checked, 0 wrong keys, 1 stem clarified and 1 rationale made more precise.

## Still needs SME review (in priority order)

1. **Chapter-check rationales (updated in pass 14).** In pass 13, 62 of the 130 ITSUP chapter-check items had a rationale that was only a section reference. All 64 such items (counted with a slightly broader rule) now have a full explanation, written from the lesson content, with the pointer kept. Keys and options are unchanged. The audit now fails if a chapter-check rationale is only a pointer. **SME: read these 64 rationales**, listed in `curriculum_v2/rationales_pass14.py`, and the 39 added in pass 15 (`rationales_pass15.py`). Pass 15 also rewrote option wording in about 88 items for length balance (`parity_pass15.py`); an SME should confirm no distractor became arguably correct. The 56 NETOPS check items already had full rationales.
2. **Certification items (474, including 59 added in pass 15) and the passes 9–10 item bank (EXPANSION).** Both are labelled *Pending SME review* in the LMS. Classes can now turn certification items off: Mastery settings → "Include certification practice items (pending SME review)".
3. **Chapter minute totals in `lessons.py` (NETOPS 1–6, 9).** These differ from the lesson sums by 50 to 75 minutes (chapter 9: 480 vs 540). Lesson plans now show lesson time. An SME should confirm the intended chapter time, including the check and labs.
4. **NETOPS chapter 9 lessons (CLI lab track)** are the shortest text in the course (978–1,473 characters). They are lab walk-throughs that send students into the simulator. This is intentional, but an SME should confirm they are enough on their own.
5. **Objectives without chapter-check items (closed in pass 14).** IT-7.4, 8.4, 9.4, 10.4, 11.4, 12.4 and 13.4 each have two new chapter-check items (Q7.10 to Q13.11). **SME: confirm these 14 items.** They are tagged *Pending SME review*, and the sources are listed per item. Four items rest on course content and local practice rather than a vendor document: Q7.10, Q7.11, Q12.10 and Q12.11. The other gap from pass 13 (15 ITSUP and 7 NETOPS objectives with no certification items) was closed in pass 15: **SME: confirm the 59 items in `curriculum_v2/cert/content/i05_gaps_p15.py`**, starting with the course-practice ones (IT-7.x, IT-12.x).
6. **Credit-hour assumptions.** The documents assume 2 lab contact hours per lab credit, 15 weeks and 34 CFR 600.2. The registrar should confirm these for the institution.
