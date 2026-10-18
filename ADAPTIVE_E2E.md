# Adaptive mastery engine: end-to-end pass (Oct 18 2026)

Branch `content`, local commits only. The server (`app.py` on :5310) used `DATABASE_URL=sqlite:////tmp/ae2e/work.db`,
a copy of `ciwt_lms.db`. `ciwt_lms.db` itself was never opened for writing, and its sha256 is still `47fabc92…7939`.
Screenshots are in `/workspace/scratch/adaptive-e2e/` (36 PNGs, `NN-<flow>-<device>.png`), with JSON results next to them.

## How it was run
- `tools/adaptive_e2e.py` (new). It uses Playwright Chromium and drives real UI flows:
  - the one-question-at-a-time chapter check
  - lesson quick checks
  - review, mastery-check and override forms
- Before each run it clears, in the copy only, three demo students' mastery rows, chapter checks, graded attempts,
  study time, lab completions and practice exams.
- Two devices:
  - **Desktop:** 1366×900.
  - **Phone:** 390×844, Android Chrome user agent, `is_mobile`, touch, DPR 3. Every interaction is a `tap()`.
- Checks on every page:
  - no horizontal scroll
  - no visible element cut off the screen edge (outside scroll containers)
  - on the phone:
    - every tap target is at least 24 px (WCAG 2.5.8, inline text links excepted)
    - the last controls are still reachable above the fixed bottom nav after scrolling to the end
- Study time is posted to `/time/study` in 120 s heartbeats, the same call the lesson page makes, so a reading pass
  does not take real minutes.

## Flows tested (both devices)
1. **Struggler (student1).**
   - Takes the chapter 1 check, choosing the tagged wrong answers. A "Fix a mix-up" step is inserted first. Its
     "Why am I seeing this?" panel names the mix-up, the evidence and "not a grade".
   - A chapter 2 lesson shows the review banner without blocking.
   - The correction page shows "The mix-up" and "What the course teaches instead", and it can be skipped.
   - The student misses the review check. The next step is **Another way to see it**, and the page delivers the
     alternate explanation.
   - The student misses again. Nothing is inserted a third time, either on the path or in the active decision log.
     The student sees the "two reviews" note with a "Message your instructor" link.
2. **Strong student (student2).**
   - Reads chapter 1, gets the lesson quick checks right and scores 10/10 on the chapter check.
   - The engine itself (not an unlock) offers the chapter 2 mastery check, with reasons ("mastered 4 of 4… never
     graded").
   - The mastery check has 8 items (2 per objective). After passing:
     - the path and the dashboard Continue go to lesson 3.1
     - chapter 2 lessons stay open
     - My mastery shows "Mastery check passed"
3. **Tester (student3).**
   - Starts the same way, then fails the mastery check (0/8).
   - The result says "not yet", not graded, and what to do next. The path stays on chapter 2.
4. **Instructor.**
   - The heatmap shows the struggler's chapter 1 cells as needs review, and the stuck list names the objective.
   - The student page shows the decision log and the mix-ups.
   - Override dialog (tapped from a heatmap cell on the phone, full-screen modal):
     - **Force review:** the student sees it first, marked Required, with the instructor's note. Opening a
       chapter 3 lesson redirects to the review, and there is no Skip.
     - **Clear** ("reset", back to the engine): the forced review is gone.
     - **Lock CH-3:** there is no chapter 3 offer, and the test-out URL is refused.
     - **Waive** on the stuck objective: the student sees "Waived", and the objective is gone from the path and
       the stuck note.
   - **Who needs me** was checked.
   - **Adaptivity off:** the path says so and shows no engine reviews. Then it was turned back on.

## Results
| Run | Before fixes | After fixes |
|---|---|---|
| `adaptive_e2e.py` desktop 1366 | 76/81 | **81/81** |
| `adaptive_e2e.py` phone 390 | 94/98 | **115/115** (the bottom-bar reachability checks were added after the first run) |
| `tools/mastery_e2e.py` (pass 11 suite) 1366 / 390 | 38/38 / — | **38/38 / 38/38** |
| axe WCAG 2.1 AA, mastery/student pages, 390+1280, light+dark | — | 56 page/width checks, **0 violations** |
| `pytest -q tests` | 556 passed, 10 skipped | **568 passed, 10 skipped** (the 10 skips are `test_vm_real.py`: v86 assets not fetched) |

Desktop before fixes: 5 failures. 3 were the real bugs 1–3 below. 2 were problems in the script itself: a wrong
selector for the dashboard hero and the wrong wording for "Mastery check passed". Those 2 were corrected in the
script, and running it against the corrected selector turned up bug 4.

There was no layout failure at either size: no horizontal scroll, nothing clipped, and no tap target under 24 px.

## Bugs found and fixed (commit 87e6ca1; tests in `tests/test_adaptive_e2e_fixes.py`)
1. **The promised alternate explanation never came for objectives with mix-ups** (`mastery/policy.py`
   `apply_misconceptions`).
   - Every review or alt review on an objective with an active mix-up was turned into a mix-up correction. So the
     second review's "Why" said *"this time the same objective is explained another way (plain-English summary,
     analogy and a worked example)"*, but the page served the mix-up correction again ("Fix a mix-up · about 2
     minutes"). Many objectives carry several mix-ups (IT-1.1 has four), so a struggling student could never reach
     the alternate explanation.
   - Now:
     - Once the student has completed any correction on the objective (the engine records the `mc:` variant of
       completed review checks as `mc_done` in history), the next review is the alternate explanation.
     - It names the mix-up that is still active, and the other corrections stay one tap away ("Fix: …").
     - If an alt review is still turned into a correction (the first review was a plain one), the false "explained
       another way" reason is removed.
2. **Stuck objectives still got a third insertion.** After two completed reviews, a repeated mix-up (seen at least 2
   times) inserted an optional correction anyway. That contradicts the rule ("not inserted again, flagged stuck") and
   the student note. On the phone it was hidden only because the path shows 3 steps. Stuck rows are now skipped.
3. **Mix-up steps on the path were missing the "Inserted before your next lesson" badge and their icon.** Their time
   also disagreed with the page: the path said "about 5 min", the page "about 2 minutes".
   - Inserted corrections now get the badge, and optional repeated-mix-up offers say "Optional" (`offer` flag).
   - The icon is `bi-lightbulb`, which is in the icon subset.
   - The time comes from one table (`engine.REVIEW_MINUTES`) that matches the review page.
4. **The dashboard showed no Continue button** once the getting-started steps had no next step (chapter check done,
   graded test not released). It showed "3 of 4 steps done" with no button, even though the adaptive path had a next
   step (lesson 3.1 after testing out). The hero now falls back to the adaptive path's next step
   (`templates/student_dashboard.html`, one `elif`).

New tests (12) also cover engine paths that had no test before:
- the strong student's route flow: engine offer → pass → next lesson moves to chapter 3, the gradebook is untouched,
  chapter 2 lessons stay open
- a forced review after a correction stays required and becomes the alternate explanation
- the attempt cap versus Unlock
- an objective-level Lock does not force a review on a mastered objective

## Needs a human / SME decision
- **The test-out threshold is strict.** A perfect 10/10 on the chapter 1 check alone does *not* earn the chapter 2
  offer. IT-1.2, IT-1.3 and IT-1.4 have only 2 items each in that check, and 2 right answers at weight 0.8 give 81%
  with n_eff 1.6, which counts as "developing". The objective needs n_eff ≥ 2 to count as mastered. One more right
  answer, such as a lesson quick check, makes it 90% and mastered, which is how the e2e strong student qualifies.
  Options:
  - keep it strict
  - add a third item per objective to the chapter checks
  - count a perfect chapter check as enough
- **Lock on a chapter skips ahead.** With CH-3 locked, the engine offers the *chapter 4* mastery check to a student
  whose next lesson is 3.1. Should a lock stop all later offers until the locked chapter is done?
- **"Reset"** is implemented as *Clear override* (back to the engine). There is no instructor action that resets a
  student's evidence on an objective. Decide whether that is wanted; it would mean ignoring real answers.
- **The time estimates are not measured:** "about 2 min" for a mix-up correction and "about 5 min" for a review or
  alternate explanation. The correction page includes two lesson sections plus 3 questions, so 2 minutes may be
  optimistic.
- ~~**The heatmap has no marker for stuck cells.**~~ Fixed in round 2 (below). A stuck cell has no "R" (nothing is inserted). Stuck is shown only
  in the "Stuck" list above the grid.
- ~~**The override dialog's status line goes stale.**~~ Fixed in round 2 (below). It describes the cell that opened the dialog and does not change
  if the instructor picks a different objective under "Applies to".
- ~~**The review page repeats the evidence.**~~ Fixed in round 2 (below). It appears both as the last "Why" bullet and as the "Evidence:" line.
- **New learner-facing wording is Pending SME review.** This pass added the two reason sentences in
  `policy.apply_misconceptions` ("Your answers still suggest this mix-up… You already worked through a mix-up
  correction here, so it is not repeated…" and "You already did one review on this objective and the estimate is
  still low."). No curriculum content was added or removed.

## Round 2 (Oct 18 2026, later)

### UI fixes (commit `a80cf2b`, tests in `tests/test_adaptive_ui_round2.py`)
1. **Stuck cells on the instructor heatmap now have a marker.**
   - A red "S" flag and a dashed outline, so the signal is not colour alone.
   - Screen-reader text ("stuck after two reviews") and a legend entry.
   - Dark-theme colours included.
2. **The override dialog's status line follows "Applies to".**
   - The heatmap and the per-student page embed status lines (`#mxStates`, JSON) for every objective and every
     "Whole chapter N" target of each student, built by `mastery.status_lines`.
   - The dialog updates the line when the target changes (`aria-live="polite"`, and the select has `aria-describedby`).
   - Chapter targets get a summary, for example "Whole chapter 1: 4 needs review (of 4 objectives) · 1 stuck".
   - Cost: about 55 KB of extra HTML on the class heatmap with the demo roster (gzip shrinks it a lot). It is not
     paginated.
3. **The review page shows the evidence once.**
   - The "Evidence:" line is dropped when one of the engine's reasons already contains it.
   - It stays when no reason carries it, for example on a self-opened practice review.

### Results (branch `content`, after merging refinement pass 14 at `22355a3`)

| Run | Round 1 | Round 2 |
|---|---|---|
| `adaptive_e2e.py` desktop 1366 | 81/81 | **92/92** (11 new round-2 checks) |
| `adaptive_e2e.py` phone 390 | 115/115 | **128/128** |
| pytest | 568 passed, 10 skipped | **595 passed, 10 skipped** |
| node --test tests/js | 40/40 | **40/40** |
| axe on mastery pages (390 and 1280, light and dark) | 56 checks, 0 violations | 40 page/width checks, **0 violation nodes** |

New round-2 e2e checks:
- evidence shown once on the mix-up correction page and on the alternate-explanation page
- stuck cell: visible S flag and outline, screen-reader text, and only stuck cells marked
- override dialog: opens with the cell's line, follows another objective, gives a chapter summary for a whole-chapter
  target, and restores the original line

Run details:
- Server: `app.py` on :5320 against `/tmp/r2/work.db`, a copy of `ciwt_lms.db`. The sha256 of `ciwt_lms.db` is
  unchanged.
- Screenshots and JSON: `/workspace/scratch/adaptive-e2e-r2/`.

### Still open for a decision
These are unchanged from round 1:
- the test-out threshold (a perfect chapter check alone is not enough for IT-1.2 to IT-1.4)
- a chapter lock skips ahead to the next chapter's offer
- "Reset" means clear the override, not reset the evidence
- the unmeasured time estimates

Pass 14 added a related gradebook change: a passed test-out now marks the chapter check "Exempt (test-out)".

Refinement later merged labs round 2/3 (`37d20d1`), and that was merged into `content` as well (`1c1518a`). It had no
conflicts and the item counts are unchanged. Results on `1c1518a`:
- pytest: 637 passed, 30 skipped. All 30 skips are `test_vm_real.py`, because the v86 assets are not in this
  worktree.
- node: 41/41.
- `adaptive_e2e`: desktop 92/92, phone 128/128.
- Readiness with `--package`: 28/28.

## Round 3 (Oct 18 2026, 05:07–05:40 UTC): misconception tags for the graded tests, spot-check round 3

A previous round-3 worker stalled at 04:58 with two untracked files. Their mtimes and sha256 did not change over a
3-minute check (05:07:37 → 05:10:27) or since 04:58, so this worker took the work over and kept it.

### Commits (branch `content`, local only)
| Commit | What |
|---|---|
| `115b85b` | Merge `refinement` `f9ffdc4` (pass 15 rationales, option-length parity, cert gap items, readiness checks) into `content`. No conflicts. |
| `548f8f8` | The stalled worker's files, committed as WIP and not wired: `tools/misconception_coverage.py`, `curriculum_v2/misconceptions_round3.py`. |
| `6cabe39` | Round 3 finished and wired into the engine (`curriculum_v2/misconceptions.py`). The correction page shows the status. Tests are in `tests/test_misconceptions_round3.py`, and before/after coverage is in `docs/readiness/misconception-coverage-round3-*.txt`. |
| `409fa84`, `508e2e2` | Semester sim: the strong-student checks were adjusted for the denser tags (see below). Documented in `docs/SEMESTER_SIMULATION.md`. |
| `493c410` | Accuracy spot-check round 3: `docs/readiness/SPOT_CHECK_ROUND3.md`, frozen sample, `--round3` sampler, one stem fix, tests. |

### Misconception tagging (rules in the `misconceptions_round3.py` docstring)
- **Tags.** 305 (item, distractor) tags. Every one was checked against the items the engine actually serves:
  - the option text matches exactly
  - it is not the key
  - its objective matches the misconception's
  - `tag_for` returns it

  The stalled worker's 90 tags were kept. Three of them pointed at chapter-check distractors that pass 15 had
  rewritten for option-length parity (Q4.7, Q4.9, Q6.7), so they were updated to the served text.
- **Misconceptions.** 91 new `MC-R3-*` entries. Each one has:
  - a primary `source` (standard, RFC, NIST, vendor documentation, or the course lesson for course procedure)
  - `status: 'Pending SME review'`, which the mix-up correction page now shows ("Status of this mix-up description:
    Pending SME review.")
  - a lesson section for its correction (tested)
- **Reuse.** 18 existing ids were reused, on 42 tags, where the wrong idea is the same. Two drafted ids were dropped in favour of
  existing ones:
  - A1.23 → `MC-C-IT8-REPAIR-TOOL`
  - NQ6.4 → `MC-C-NO6-NO-ROLLBACK`
- **Left untagged on purpose:**
  - Q13.6 and NQ5.5: their distractors are throw-aways, not a wrong idea the explanation names.
  - Single throw-away distractors on items that are otherwise tagged, such as "Reset every user's password" on A1.32.
- **Label edit.** One draft label was narrowed: `MC-R3-IT8-DESTRUCTIVE-FIRST` no longer lists "convert", because
  MBR2GPT is non-destructive.

Coverage, measured with `tools/misconception_coverage.py` on a throwaway DB. Before is `548f8f8`, merged but not
wired; after is `6cabe39`.

| | Before | After |
|---|---|---|
| Objectives covered | 70/70 | 70/70 |
| Tagged scorable distractors | 883/2349 | **1188/2349** |
| Items with ≥ 1 tagged distractor | 381/783 | **495/783** |
| Tests A/B/C (single-answer) | 30/129 | **129/129** |
| Chapter checks | 183/200 | **198/200** (Q13.6, NQ5.5 untagged) |
| Cert / X-IT bank / supplement | 168/293, 0/131, 0/30 | unchanged |
| Objectives with only one correctable misconception | IT-2.3, IT-11.3, NO-6.1 | none |

### Semester simulation: a behaviour change caused by the denser tags (decision needed)
With Tests A/B/C tagged, strong synthetic student 31 picked the same mix-up twice: `MC-IT4-SWOLLEN-HANDS-ON`. The
engine recorded the two hits on one simulated day, from a daily review and a review check. So "Who needs me" and the
briefing focus listed them last, with severity 0, under "Picked the same mix-up 2 times". That is the engine's rule.
Two sim checks had said "no strong student". They now say a strong student may appear only for a repeated mix-up and
only below every weak, mixed and disengaged student. The run is 15/15, and `strong_in_needs_me` in the JSON records who
appeared. **No engine rule was changed.**

### Results on `493c410` (final)
| Run | Result |
|---|---|
| `pytest -q tests` | **653 passed, 30 skipped**. All 30 skips are `test_vm_real.py`: the v86 assets are not in content-wt. |
| `node --test tests/js` | **41/41** |
| `adaptive_e2e.py` desktop 1366 | **92/92** |
| `adaptive_e2e.py` phone 390 | **128/128** |
| Round-3 correction page (`IT-5.3?mc=MC-R3-IT5-DUPLEX`), 1366 and 390 | HTTP 200, label and Pending SME status shown, no horizontal scroll |
| `curriculum_readiness.py --package` | **30/30**. Refinement added two checks since round 2. |
| `semester_sim.py --days 28` | **15/15** |

Run details:
- The earlier run on `6cabe39`, before the spot-check, was also 92/92 and 128/128. The first full pytest on `6cabe39`
  had 1 failure, the semester sim; the fix is above.
- Server: `app.py` on :5291 against `/tmp/r3/work2.db`, a copy of `ciwt_lms.db`. The server is stopped.
- Screenshots and JSON: `/workspace/scratch/adaptive-e2e-r3-final/`.
- Readiness JSON: `/workspace/artifacts/pass-reports/readiness-content-round3.json`.

### Spot-check round 3 (60 original items, no certification items; checked by Grok Bot, not an SME)
- **0 wrong answer keys. No key was changed.**
- **1 stem fixed: X-IT-9.2.3.** "from their Mac" made "the device owner" ambiguous. The stem now says the Mac is
  college-owned. *Pending SME review*.
- **SME notes, no change:**
  - X-IT-6.3.3: Microsoft also names the checkpoint-file volume for Paused-Critical.
  - X-IT-8.1.1: "Fix problems using Windows Update" is hidden on managed PCs.
- **Thin rationales.** 23 ITSUP chapter-check items still have a one-line rationale under 90 characters, listed in
  `SPOT_CHECK_ROUND3.md`. Pass 15 did not reach them because they carry their study tip as their review rationale.

### Course package
Rebuilt from `493c410`, with a clean tree:
- `/workspace/artifacts/course-package-content/`: 45 files including the MANIFEST
- `/workspace/artifacts/course-package-content.zip`: 52 entries

The answer keys contain the X-IT-9.2.3 fix. The ITSUP answer key PDF has 147 "Pending SME review" labels and the
NETOPS one has 1. Refinement's `/workspace/artifacts/course-package/` was not touched.

`ciwt_lms.db` sha256 is `47fabc92…7939` in `/workspace/ciwt/ciwt-lms`. content-wt has no `ciwt_lms.db`, because it is
git-ignored. All runs used `/tmp/r3/*.db` copies.

### Open questions for a human (none decided here)
1. **Test-out bar.** A perfect chapter 1 check alone does not reach mastery on IT-1.2 to IT-1.4 (2 items each, n_eff
   1.6 < 2). Options: keep it strict, add a third item per objective, or accept a perfect check.
2. **Chapter lock skips ahead.** With CH-3 locked, the engine offers the chapter 4 mastery check. Should a lock stop
   later offers?
3. **"Reset"** means clear the override. Should there be an evidence reset? That would ignore real answers.
4. **Time estimates are unmeasured:** 2 min for a mix-up correction, 5 min for a review.
5. **Heatmap payload.** The status-line JSON adds about 55 KB with the demo roster and grows with class size ×
   objectives. Is that acceptable, or should it load on demand?
6. **Thin rationales.** 23 ITSUP chapter-check items, down from the 61 counted in round 2. Write full ones next?
7. **(new) Repeated mix-up on a strong student.** Should "picked the same mix-up 2 times" list a student whose other
   evidence is strong? It appears last, at severity 0. With the graded tests now tagged, it will happen more often.
   Options:
   - keep it
   - require 3 hits
   - require the objective to be below mastered
8. **(new) Reused fix text.** Some reused pass-13 ids carry an item-specific fix. For example, `MC-IT5-PORT-SERVICE`'s
   fix says "Port 53 is DNS". It now also fires on A1.16, the port 445 item, so the correction's one-line fix names a
   different port than the student's question. An SME may want generic fix text on reused ids.
9. **SME review** of the 91 new round-3 misconception labels, fixes and sources, all *Pending SME review*.

## Round 4 (Oct 18 2026, 06:08–06:45 UTC): full rationales, cert-gap misconception tags, spot-check round 4

Same worktree (`/workspace/ciwt/content-wt`), branch `content`, port 5291. Local commits only, nothing pushed or
merged. The refinement repo, port 5078, labs-wt and port 5191 were not touched.

### Commits (branch `content`, oldest first, on top of `df46e29`)
| Commit | What |
|---|---|
| `fa0fa2f` | Full rationales for the 23 thin ITSUP chapter-check items, plus NQ5.5 (`curriculum_v2/rationales_round4.py`). Wired in `item_review.review_check` and `netops_quiz_payload`. Tests: `tests/test_rationales_round4.py`. |
| `fd31dc0` | Misconception coverage for the pass-15 cert gap items and the last two untagged chapter checks (`curriculum_v2/misconceptions_round4.py`), wired into `curriculum_v2/misconceptions.py`. `tools/misconception_coverage.py` now reports the pass-15 subset. Before/after: `docs/readiness/misconception-coverage-round4-*.txt`. Tests: `tests/test_misconceptions_round4.py`. |
| `464f181` | `curriculum_v2/cert/alignment.json` and `CERT_COVERAGE.md` regenerated. `test_alignment_json_is_up_to_date` failed after `fa0fa2f`, because the keyword mapper reads rationale text (see below). |
| `c006e6c` | Spot-check round 4: `docs/readiness/SPOT_CHECK_ROUND4.md`, frozen sample, `--round4` sampler, AM5 lesson fix, citation erratum, tests (`tests/test_spot_check_round4.py`), and a `CURRICULUM_READINESS.md` line. |

### 1. Thin chapter-check rationales: 23 → 0
- **Measure (same as round 3).** A served rationale under 90 characters that starts with a section pointer
  ("1.1 — …", "2.1 / hw-board card — …").
  - Before: 23/200 chapter-check items, all ITSUP: Q1.0, Q1.1, Q1.5, Q1.6, Q1.8, Q2.0, Q2.1, Q2.2, Q2.4, Q2.5, Q2.6,
    Q2.8, Q4.0, Q4.2, Q4.3, Q4.6, Q5.7, Q6.0, Q6.1, Q6.6, Q6.7, Q7.0, Q7.3.
  - After: **0/200**, measured on the quiz payloads and on the engine's course map (what students are served).
- **What each rationale does.**
  - Says why the key is right and why each distractor is wrong, using what the cited lesson teaches.
  - Keeps the original "See x.y" pointer, and the served text ends "Source: …" with a primary source. The sources
    are ITIL 4 practice guides, the Intel ATX/microATX specs, EIA-310, JEDEC, UEFI 2.10, Microsoft Learn, U.S. EPA,
    CISA, NIST SP 800-125, Broadcom KB 1025279 and IETF RFCs. Where the item tests the course's own lab command, the
    course card is the source.
- **Status.** Each item's `review` now says "rationale rewritten in content round 4 …; Pending SME review".
- **Tests** (`tests/test_rationales_round4.py`):
  - zero thin items, in the payloads and in the engine
  - keys unchanged against a frozen list
  - at least 45 words per rationale
  - every distractor's distinctive word appears in its rationale
  - pointer kept, source appended, status Pending
- **NQ5.5 rationale extended.** Its "removes the need for SNMP" distractor gained a tag (below), so the rationale now
  explains syslog vs SNMP.
- **Unchanged.** No key, stem or option changed: all 200 items were compared before and after, and only the 24
  rationales differ.
- **Side effect: cert alignment.** `tools/cert_coverage.py` maps items to exam objectives by keyword hits in stem,
  options and rationale, so longer rationales moved 5 items within their curated candidates:
  - Q1.0: A2:4.1 → A2:4.2
  - Q1.1 and Q1.8: + A2:4.2
  - Q2.2: + A1:3.4
  - Q4.2: + A2:2.8

  Coverage is still 100% on A+ Core 1, Core 2 and Network+. Q1.0 (service-request classification) now maps only to
  change management, which is a worse fit. It is a heuristic artefact, left as measured (open question 10).

### 2. Misconception tags: pass-15 cert gap items and the last chapter checks
The brief assumed the 59 pass-15 items were untagged. Measured, they were not:
- Pass 15 wrote `mc=` tags in `i05_gaps_p15.py`, and they already reached the engine through
  `curriculum_v2.cert.misconceptions`.
- 155 of the 165 distractors on the 55 single-answer items were tagged. All 155 verified against the served items:
  - the option text matches exactly
  - it is not the key
  - the objective matches
  - `tag_for` returns it
- The gap was elsewhere:
  - 10 distractors had no tag
  - none of the 47 pass-15 `MC-C-*` misconceptions had a `source` or a `status`, so the correction page did not say
    they are unreviewed
  - the 2 choose-N and 2 ordering items are not scored per distractor by the engine (same as every bank)

Done:
- **Five new tags on pass-15 distractors** whose wrong idea the item explanation names:

  | Item | Distractor | Tag |
  |---|---|---|
  | C-A2-4.1-105 | "Order another 8 GB module" | `MC-C-IT2-RECONCILE-SKIP` |
  | C-A1-2.6-101 | "An administrator set a static address" | `MC-C-IT5-APIPA` |
  | C-N-5.1-103 | "Escalate all three to the network team at once" | `MC-C-IT7-BUNDLE` |
  | C-A2-4.3-102 | "Three backups a day, two admins, one restore test" | new `MC-R4-IT12-321-COUNTS` |
  | C-N-3.4-105 | "The DHCP server for its scope" | new `MC-R4-NO4-DHCP-RESOLVES` |

  Five throw-aways stay untagged. They are listed in the module docstring.
- **Source and status on the 47 pass-15 misconceptions.**
  - `source` is the distinct primary sources pass 15 recorded for the items carrying each tag (`i05_gaps_p15.SOURCE`).
  - `status` is `Pending SME review`.
  - The correction page now shows the status. Checked in a test, and in a browser at 1366 and 390 on
    `IT-1.1?mc=MC-C-IT1-REQ-VS-INC`.
- **Last two chapter checks.**
  - Q13.6: "Hyper-V delete-all, snapshots, vSwitch, uplinks" → `MC-IT13-CHANGE-BEFORE-STATE`. Its rationale names
    deleting snapshots as the unsafe move.
  - NQ5.5: "It removes the need for SNMP" → new `MC-R4-NO5-LOG-VS-SNMP`.
- Each of the 3 new `MC-R4-*` entries has a primary source and Pending SME review, and finds a lesson section for its
  correction (tested).

Coverage, measured with `tools/misconception_coverage.py` on a throwaway DB. Before is `df46e29` (an archive of the
tree, run with the new tool); after is `c006e6c`.

| | Before | After |
|---|---|---|
| Objectives covered | 70/70 | 70/70 |
| Tagged scorable distractors (all banks) | 1188/2349 | **1195/2349** |
| Items with ≥ 1 tagged distractor | 495/783 | **497/783** |
| Chapter checks with ≥ 1 tag | 198/200 | **200/200** |
| Tests A/B/C | 129/129 | 129/129 |
| Pass-15 single-answer items served / with ≥ 1 tag | 55/55 / 55/55 | 55/55 / 55/55 |
| Pass-15 served distractors tagged | 155/165 | **160/165** |
| Pass-15 misconceptions with source / status | 0/47 / 0/47 | **47/47 / 47/47** |
| All misconceptions with a status | 91/400 | 141/403 |

Not covered by this round:
- The X-IT bank (0/131) and the exam supplement (0/30) are still untagged.
- The 262 misconceptions from passes 11, 13 and 14 still have no `status`, so their correction pages show no Pending
  line. For example, `MC-IT13-CHANGE-BEFORE-STATE` was checked on the page and shows none.

### 3. Spot-check round 4 (60 original items, no certification items; checked by Grok Bot, not an SME)
Details are in `docs/readiness/SPOT_CHECK_ROUND4.md`. The frozen list is `spot-check-round4-sample.json`, drawn with
`--round4 16`. It excludes rounds 1–3, puts the least-checked objectives first, covers every chapter, and has 60
objectives. Pools:

| Pool | Items |
|---|---|
| ITSUP checks | 25 |
| X-IT bank | 11 |
| A1 | 8 |
| N1 | 6 |
| NETOPS checks | 4 |
| supplement | 2 |
| N2 | 2 |
| A2 | 1 |
| A3 | 1 |

- **0 answer keys changed. 0 stems changed. 0 rationales changed.**
- **1 key disputed, sent to an SME: Q9.11.**
  - The item: a Linux share holds Plan.docx and plan.docx, and the key says Windows "shows only one". Lesson 9.4
    says the same.
  - `smb.conf(5)` documents caseless name matching for Windows clients.
  - Samba community sources and user tests report that Explorer and `dir` list both names, and opening either one
    opens the first match. So the key is probably inaccurate about what a user sees.
  - Not changed: no official primary source covers listing, and it needs a test with a real Windows client. A
    suggested rewrite is in the doc.
- **SME notes, no change:**
  - Q8.3: the key's wording.
  - X-IT-5.3.1: some gateways do not answer ping.
  - A1.48: Sysprep does not fix a static IP baked into the image.
  - Q1.6 and Q12.0: near-duplicates.
- **Lesson fact fixed (outside the sample, found while writing Q2.1's rationale).** Lessons 2.1 and 2.3
  (`block2_hardware.py`) said "AMD AM4/AM5: pins on the CPU". AMD's AM5 quick reference guide says "1718-pin LGA
  socket", so it now says AM5 is LGA. *Pending SME review.*
- **Citation erratum.** CompTIA's 220-1201 objectives document says the troubleshooting methodology "does not
  constitute a formal objective". 220-1201 objective 5.1 is motherboards, RAM, CPUs and power.
  - Fixed: three round-3 misconception sources and two round-4 sources had cited "220-1201 objective 5.1".
  - Not edited: `SPOT_CHECK_ROUND3.md` is the round-3 record. Its rows A1.38, A3.0 and X-IT-7.1.1 carry the same
    mis-citation; their verdicts are unaffected.

### Results on `c006e6c` (final)
| Run | Result |
|---|---|
| `pytest -q tests` | **671 passed, 30 skipped**. All 30 skips are `test_vm_real.py`: the v86 assets are not in content-wt. Round 3 was 653 passed; round 4 adds 18 tests. |
| `node --test tests/js` | **41/41** |
| `adaptive_e2e.py` desktop 1366 | **92/92** |
| `adaptive_e2e.py` phone 390 | **128/128** |
| Round-4 correction pages, 1366 and 390 | HTTP 200, label shown, "Pending SME review" status shown, no horizontal scroll. Pages: `IT-12.3?mc=MC-R4-IT12-321-COUNTS` and `IT-1.1?mc=MC-C-IT1-REQ-VS-INC`. |
| `curriculum_readiness.py --package` | **30/30**. The key is uniquely the longest option in 31/200 chapter checks (15.5%), unchanged. |
| `semester_sim.py --days 28` | **15/15**. `strong_in_needs_me` is `[31, misconception]`, the same as round 3. |

Run details:
- During the round, a mid-run pytest showed one failure, `test_alignment_json_is_up_to_date`, after `fa0fa2f`. It was
  fixed in `464f181`, and the next full run was 666 passed.
- Server: `app.py` on :5291 (PID 1088812) against `/tmp/r4/e2e.db`, a copy of `ciwt_lms.db`. It was stopped by PID,
  and port 5291 is free.
- Readiness used `/tmp/r4/ready2.db` and the sim used `/tmp/r4/sim.db`. Both are copies.
- Screenshots and JSON: `/workspace/scratch/adaptive-e2e-r4-final/`.
- Readiness JSON: `/workspace/artifacts/pass-reports/readiness-content-round4.json`.

### Course package
Rebuilt from `c006e6c`, with a clean tree:
- `/workspace/artifacts/course-package-content/`: 45 files including the MANIFEST, the same file set as round 3
- `/workspace/artifacts/course-package-content.zip`: 52 entries, written with Python `zipfile`, because `zip` is not
  installed

"Pending SME review" labels in the answer-key PDFs:

| Answer key | Round 3 | Round 4 |
|---|---|---|
| ITSUP | 147 | **170** (+23 rewritten rationales) |
| NETOPS | 1 | **2** (+NQ5.5) |
| CLIENT | — | 87 |

The old one-liners are gone from the ITSUP key. Readiness `--package` matched every MANIFEST hash. Refinement's
`/workspace/artifacts/course-package/` was not touched.

`ciwt_lms.db` sha256 is still `47fabc92dafe16cf128b34e90c8235d61d02bc735738a83b8a6172fb93597939`.

### Open questions for a human (round 4 additions; round-3 questions 1–9 still open)
10. **Cert alignment heuristic.** Longer rationales move items between curated exam objectives, for example Q1.0 →
    change management only. Options: pin chapter-check items with a curated item map, or score the stem and options
    only.
11. **Q9.11 / lesson 9.4.** Test Plan.docx/plan.docx on a real Windows client against Samba, then either keep the
    key or apply the suggested rewrite (stem, key and lesson clause).
12. **Pending status on older misconceptions.** 262 of 403 have no `status`. Should passes 11/13/14 also show
    "Pending SME review" on the correction page?
13. **SME review of round 4 content:**
    - the 24 rationales and their sources
    - the 3 `MC-R4-*` entries
    - the derived sources on the 47 pass-15 misconceptions (some list several item sources, for example
      `MC-C-IT1-REQ-VS-INC` also cites the change-management objective)
    - the AM5 lesson correction
14. **X-IT bank and supplement** (161 items) still have no misconception tags. Is that the next tagging target?

## Round 5 (Oct 18 2026, ~07:00–07:50 UTC): X-IT bank and supplement misconception tags, bank-on e2e, spot-check round 5

Worktree `/workspace/ciwt/content-wt`, branch `content`, local commits only (nothing pushed). Every run used a copy of
`ciwt_lms.db` under `/tmp/r5/`. Checked by Grok Bot, not an SME; all new content is tagged "Pending SME review".

### Commits (branch `content`, oldest first, on top of `23b427f`)
| Commit | What |
|---|---|
| `3b84c79` | Misconception tags for the X-IT bank and exam supplement: `curriculum_v2/misconceptions_round5.py` (66 new `MC-R5-*` entries, 348 tags), the coverage tool's bank/supplement report, before/after files, `tests/test_misconceptions_round5.py`, and a fix to `tests/test_mastery_features.py` (its helper did not know the bank items) |
| `f4b426d` | Spot-check round 5: sampler `--round5`, frozen sample, `docs/readiness/SPOT_CHECK_ROUND5.md`, `tests/test_spot_check_round5.py`, a line in `CURRICULUM_READINESS.md` |
| `3e96b8e` | Bank-on e2e flow in `tools/adaptive_e2e.py`, `--bank` mode in `tools/semester_sim.py`, and 2 tests |
| (this commit) | This round-5 section in `ADAPTIVE_E2E.md` |

### 1. Misconception tags for the X-IT bank (131 items) and exam supplement (30 items)
Rules and sourcing are the same as in rounds 3–4:
- A tag goes only on a served distractor that reflects a nameable mix-up for the item's own objective.
- Existing ids are reused only when their fix text fits the item. Where the fix names a different port, number or
  procedure, I added a new `MC-R5-*` entry instead, for example `MC-R5-IT5-SMB-PORT` rather than `MC-C-IT5-PORT-MIX`.
- Every new entry has a primary source (vendor docs, RFCs and standards from the pass 9/10 source registry), or a course
  chapter section cited by its heading. I removed uncertain clause and section numbers instead of guessing them.
- The status of every new entry is "Pending SME review", and the correction page shows it.

Measured with `tools/misconception_coverage.py`. The before file was made with the round-4 tool at `23b427f`.

| | Before (`round5-before.txt`) | After (`round5-after.txt`) |
|---|---|---|
| Objectives covered | 70/70 | 70/70 |
| Tagged distractors | 1195/2349 | **1543/2349** (+348) |
| Items with ≥1 tagged distractor | 497/783 | **634/783** |
| X-IT bank items | 0/131 | **110/131** |
| Supplement items | 0/30 | **27/30** |
| Cert / chapter checks / tests | 168/293, 200/200, 129/129 | unchanged |

- New entries: 66 `MC-R5-*` (66 sourced, 66 Pending, and each finds a lesson section for its correction page). 71
  existing ids were reused.
- 24 items are left untagged on purpose, because their distractors are not a nameable mix-up or no fix text fits:
  S-IT-2.4.2, S-NO-6.3.2, S-IT-9.2.1, X-IT-3.1.3, 3.3.4, 3.4.1, 4.1.2, 4.2.3, 6.1.3, 7.1.2, 7.4.2, 8.2.3, 9.2.2,
  9.4.2, 10.2.3, 11.2.1, 11.2.3, 11.3.3, 11.4.1, 11.4.2, 12.3.1, 13.1.3, 13.2.2, 13.3.1. They are listed in
  `misconceptions_round5.UNTAGGED`, and a test pins the list.
- No item stem, option, key or rationale changed. Cert alignment and the course package are unaffected: all 22
  document-model hashes are identical to round 4.

**Where the new tags take effect (checked in code).** X-IT and S- items reach students only through review checks and
mastery checks, and only when the class turns on "Also use the chapter item bank" (`testout_bank`). That setting is
**off by default**. Graded knowledge tests use A1/A2/A3/N1/N2/N3 items, which I checked in the DB copy, and practice
exams use cert items. So with default settings the round-5 tags change nothing a student sees.

### 2. Adaptive engine re-verification after the new tags
New e2e flow (`tools/adaptive_e2e.py`, between the instructor flow and the final error check):
1. The instructor turns the bank on through the settings route.
2. The tester opens the correction for `IT-5.2?mc=MC-R5-IT5-DORA`. The label "Mixing up the order of the DHCP
   exchange" and "Status of this mix-up description: Pending SME review." are shown, with no horizontal scroll and
   nothing clipped.
3. The check leads with the tagged bank item X-IT-5.2.2: served `['X-IT-5.2.2', 'Q5.5', 'Q5.6']`.
4. The tester answers "Discover" on it and submits. Who needs me (today) then shows the row "Mixing up the order of the
   DHCP exchange · IT-5.2 · 1 student · 1 pick · 1 open". The briefing loads with the bank on.
5. With the bank turned off again, the correction check serves no X-/S- item, for example
   `['C-A1-2.1-21', 'C-A1-2.1-23', 'C-A1-2.3-2']`. The settings are restored.

`tools/semester_sim.py --bank` turns the bank on for the synthetic class through the real settings route. In both
modes it now records the bank items served. Bank mode adds two checks: bank items were served, and every tagged wrong
answer on them is recorded as that mix-up in the student's state. Default mode adds one check: no bank item is served.

**Bugs found: none.** Two tests now make the behaviour above permanent:
- `test_with_the_bank_on_a_round5_correction_serves_its_bank_item_and_records_the_mixup`
- `test_semester_simulation_with_the_bank_on` (14 days, bank checks only)

The default sim test also asserts that the bank is off and nothing was served.

Semester sim, 28 days, seed 13. Synthetic cohort: this tests engine behaviour, not learning gains.

| Mode | Checks | Bank items served | `strong_in_needs_me` |
|---|---|---|---|
| default (bank off) | **16/16** | 0 | `[31, misconception]`, the same as rounds 3–4 |
| `--bank` | **18/18** | 226 servings of 43 distinct items, 67 tagged wrong answers, all recorded | `[]` |

Observation, not a round-5 regression: at `--days 14`, 4 of the sim's 28-day checks fail in **both** modes. Strong
students have no test-out yet, the disengaged students are not yet flagged inactive, and two strong students show
`missed_review`. These checks are written for the documented 28-day window, so the new bank test asserts only the bank
checks.

### 3. Spot-check round 5 (60 original items, rounds 1–4 excluded; checked by Grok Bot, not an SME)
- Sample: `tools/spot_check_sample.py --round5` (seed 17), frozen in `docs/readiness/spot-check-round5-sample.json`.
  The 220 ids from rounds 1–4 are excluded.
- Pools: EXPANSION 18, ITSUP checks 17, NETOPS checks 10, supplement 6, N1 3, N2 3, A1 2, A2 1.
- **All 60 items are correct as served. 0 keys, stems, options or rationales changed.** Each verdict cites a primary
  source; see `SPOT_CHECK_ROUND5.md`.
- SME notes, not errors:
  - X-IT-8.3.2 assumes a restore point exists (System Protection on).
  - NQ2.1's rationale credits BPDU Guard, but STP itself already blocks the loop.
- Outside the sample, found while tagging: **X-IT-11.3.3** has the distractor "When the fault has a known, documented
  vendor fix", which its own explanation says "would also favour repair". That may make it a second defensible
  answer. Flagged, not changed, and a test records it. Suggested replacement distractor: "When the device is under
  warranty".

### Results on `3e96b8e` (final code; the docs commit on top changes only this file)
| Run | Result |
|---|---|
| `env -u PYTHONHASHSEED pytest -q tests` | **686 passed, 30 skipped**. All 30 skips are `test_vm_real.py`: the v86 assets are not in content-wt. Round 4 was 671; round 5 adds 15 tests (10 tag, 4 spot-check, 1 sim). |
| `node --test tests/js` | **41/41** |
| `adaptive_e2e.py` desktop 1366 | **107/107** (round 4: 92; +15 bank-flow checks) |
| `adaptive_e2e.py` phone 390 | **151/151** (round 4: 128; +23, including the layout checks) |
| `curriculum_readiness.py --package` | **30/30**. The key is uniquely the longest option in 31/200 chapter checks (15.5%), unchanged. |
| `semester_sim.py --days 28` | **16/16** (bank off), **18/18** (`--bank`) |

Run details:
- Server: `app.py` on :5291 against copies of `ciwt_lms.db`. The first run used `/tmp/r5/e2e.db` (PID 1124992); the
  final run used `/tmp/r5/e2e-final.db` (PID 1136239). Both were stopped by PID, and port 5291 is free.
- Readiness used `/tmp/r5/ready.db`. The sims used `/tmp/r5/sim.db` and `/tmp/r5/simbank.db`. All are copies.
- Screenshots and JSON: `/workspace/scratch/adaptive-e2e-r5-final/`. The new shot is
  `20-tester-round5-bank-mixup-{desktop-1366,phone-390}.png`.
- Readiness JSON: `/workspace/artifacts/pass-reports/readiness-content-round5.json`.
- Sim JSON: `semester-sim-content-round5.json` and `semester-sim-content-round5-bank.json`, in the same folder.

### Course package
Rebuilt from `3e96b8e`, with a clean tree (`dirty_files: []`):
- `/workspace/artifacts/course-package-content/`: 45 files including the MANIFEST, the same file set as round 4
- `/workspace/artifacts/course-package-content.zip`: 52 entries, written with Python `zipfile`

All 22 document-model hashes are identical to the round-4 build. "Pending SME review" labels in the answer-key PDFs are
unchanged: ITSUP 170, NETOPS 2, CLIENT 87. Readiness `--package` matched every MANIFEST hash. Refinement's
`/workspace/artifacts/course-package/` was not touched.

`ciwt_lms.db` sha256 is still `47fabc92dafe16cf128b34e90c8235d61d02bc735738a83b8a6172fb93597939`.

### Open questions for a human (round 5 additions; questions 1–13 from rounds 3–4 still open, 14 answered by this round)
15. **SME review of round 5 tagging:** the 66 `MC-R5-*` entries (label, fix text, source) and the 348 tags,
    especially the 71 reused ids. One known loose fit: `MC-NO9-VLAN-CREATE-ONLY` is reused on a vlan 30 item, but its
    fix text says "vlan 20".
16. **The 24 untagged bank/supplement items.** Leave them untagged, or rewrite their distractors so they carry
    nameable mix-ups?
17. **X-IT-11.3.3, a possible second defensible answer.** Replace the distractor (suggested: "When the device is under
    warranty"), or keep it?
18. **Spot-check SME notes:** X-IT-8.3.2 (restore-point assumption) and NQ2.1 (BPDU Guard vs STP in the rationale).
19. **Bank default.** The round-5 tags only reach students when a class turns on "Also use the chapter item bank",
    which is off by default. Should the default change, or should the setting be surfaced more prominently to
    instructors?
