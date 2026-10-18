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
