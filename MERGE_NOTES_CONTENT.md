# Merge notes: `content` into `refinement`

`content` branched from `refinement` at `bc19ca8`. Since then, `refinement` has moved on to `973fb66`, which includes the
labs merge. A dry run (`git merge-tree --write-tree refinement content`) auto-merges `app.py`, `templates/lesson.html` and
`templates/staff_sidebar.html`. Three files conflict, and each conflict is a simple union:

| File | Conflict | Resolution |
|---|---|---|
| `tools/a11y_sweep.py` | Both branches added entries to the `PAGES` lists (refinement: labs and mastery pages; content: practice, coverage and cert-lesson pages, plus the `@practice-take` / `@practice-result` handling in the page loop) | Keep both sets of entries, and keep content's `@practice` branch in the `try:` block. |
| `tools/site_audit.py` | Both branches added student and instructor pages (refinement: mastery pages; content: practice and cert pages, plus `practice_prep()` and the `ptake` / `presult` ids) | Keep both sets of entries and the prep helper. |
| `static/vendor/bootstrap-icons/1.11.3/bootstrap-icons-subset.css` (+ woff2) | Each branch regenerated the icon subset | Take either side, then run `python tools/build_icon_subset.py` so the subset covers the union of icons. Content needs `arrow-up`, `arrow-down`, `patch-check` and `stopwatch`. Then delete the stale `bootstrap-icons-subset-*.woff2` files. `tests/test_ux.py::test_icon_subset_covers_every_icon_used` checks the result. |

## What content changes in shared files

- `app.py` (2 small edits):
  - `_PUBLIC_ITEM_FIELDS` gains `type`, `prompts` and `choose`. These are presentation metadata for typed items; no keys are exposed.
  - `curriculum_v2.cert.practice.register(...)` is called after the materials module. It adds `PracticeAttempt`
    (table `practice_attempt`) and the routes `/staff/cert-coverage`, `/practice`, `/practice/start`, `/practice/attempt/<id>`
    and `/practice/attempt/<id>/result`.
- `curriculum_v2/apply.py`: `apply_cert(pack, course)` runs at the end of `apply_itsup` and `apply_netops`.
  - It appends 33 `<section class="sublesson cert-supplement">` blocks to existing lessons and deletes nothing.
  - CLIENT inherits the ones in ITSUP chapters 8–13.
  - If the mastery engine (`mastery/content.py`) segments lesson HTML, check that it handles the extra sections. They use the same `sublesson` class as the pass-9/10 additions.
- `curriculum_v2/documents.py`: adds cert alignment to the syllabus and lesson plans, pass-11 items to the answer keys, and supplement terms to the glossary. The data comes from `curriculum_v2/cert/package.py`. `course_package.py` is not modified, so refinement's edits to it merge cleanly.
- `static/js/assessment.js` and the new `static/js/pbq-core.js`: the multi, order and match renderers are only used when a question has `type`. Quiz and test pages are unchanged (36/36 node tests, 43/43 assessment phone e2e).
- `static/css/ciwt-theme.css` (site-wide accessibility fixes):
  - answered question chip contrast is now 5.6:1 (was 3.1:1);
  - `code` inside `.worked` boxes is now 4.5:1 or better in light mode;
  - `.lesson-prev` wraps long titles at 390 px.
- `templates/lesson.html`: adds the `lesson-prev` class to the previous-lesson button.
- `templates/staff_sidebar.html`: adds "Certification coverage" and "Practice exams" for staff, and "Practice exams" in the student Practice tree.

## After merging

1. `python tools/cert_coverage.py && python tools/cert_coverage_md.py`. This is needed because refinement's lesson changes (misconceptions, lab additions) can shift the keyword coverage. The `test_alignment_json_is_up_to_date` and `test_cert_coverage_md_is_current` tests fail until it is run.
2. `python -m pytest -q tests/` and `node --test tests/js/`.
3. On first boot against the real DB:
   - `init_db()` creates `practice_attempt`;
   - `sync_curriculum` rewrites lesson HTML with the supplements.
   Take a backup of `ciwt_lms.db` first. Content never booted against it; every run used a copy.
4. Rebuild the course package: `python tools/build_course_package.py /workspace/artifacts/course-package`. Content wrote its build to `/workspace/artifacts/course-package-content/` (and `.zip`) so it did not overwrite the existing package.

## Round 2 (commits after the first merge)

New files only, apart from the edits listed below, so the merge should be mechanical:

- `curriculum_v2/cert/content/s24_cables.py`, `s25_phys_security.py`, `s26_change_safety.py`, `s27_policy_prof.py`,
  `s28_net_appl_docs.py` — 8 new lesson sections (ITSUP 3.4, 10.1, 12.1, 1.2, 12.2, 1.4; NETOPS 4.3, 6.3), Pending SME review.
- `curriculum_v2/cert/content/i02_depth_a1.py`, `i03_depth_a2.py`, `i04_depth_n.py` — depth items (8+ per objective).
- `curriculum_v2/cert/misconceptions.py` — misconception tags for cert items in refinement's schema
  (`MISCONCEPTIONS[id] = {obj, label, fix, terms}`, `TAGS[(bank_id, distractor)] = id`, same `tag_for` contract). Ids are
  `MC-C-*`, so they cannot collide with refinement's `MC-IT*` / `MC-NO*`. Content did **not** edit refinement's
  `curriculum_v2/misconceptions.py`. To make the engine see them after the merge, add after `TAGS = {...}` there:

  ```python
  from curriculum_v2.cert import misconceptions as _cert_mc
  MISCONCEPTIONS.update(_cert_mc.MISCONCEPTIONS)
  TAGS.update(_cert_mc.TAGS)
  ```
  (before `_NORM` is built). The tags only fire for items the engine actually serves; cert items are in the
  practice-exam pool, so wiring them into `mastery/` pools is a refinement decision.
- Edited: `curriculum_v2/cert/authoring.py` (new sources; optional `mc=` on `single`/`multi`), `mapping.py` (weighted
  covered capped at 100%), `tools/cert_coverage_md.py` (round-2 section and quality log), `tools/a11y_sweep.py` (8 new
  lesson pages; coverage filter now `status=covered`), `tests/test_cert_alignment.py` (3 new tests, filter test updated).
  The `a11y_sweep.py` page lists conflict the same way as before: keep both sets.
- Item dicts now carry an `mc` key. `practice.public_item` and `app._PUBLIC_ITEM_FIELDS` are allow-lists, so it never
  reaches the browser (tested).

## Round 3: `content` at `b6a32e3` into `refinement` (pass 15)

`content` had last taken `refinement` at `37d20d1` (labs round 2/3), in `1c1518a`. Since the previous content merge,
`content` added the following, all of it merged locally and nothing pushed:

- the adaptive UI round 2: stuck marker on heatmap cells, override dialog status line, evidence shown once;
- the adaptive e2e tool and `ADAPTIVE_E2E.md`;
- accuracy spot-check round 2: 60 items, 0 wrong keys, 4 stems fixed (A2.17, N1.20, NQ1.1, NQ4.5) and 4 rationales
  made precise;
- a fresh-DB fallback in `tests/test_assess_phone_e2e.py`.

`refinement` had moved on to `c124f12` (sim reproducibility, pass 14 notes).

- **Conflicts:** none. `git merge-tree` and the real merge both auto-merged.
- **Shared files checked by hand:**
  - `curriculum_v2/item_review.py`: content's precise rationales and stem guards sit next to refinement's pass-14
    `RATIONALE` merge, which applies only where a `why` is empty, so content's text wins where both exist.
  - `tests/test_assess_phone_e2e.py`: content's seed-a-new-DB fallback works with refinement's `own_server()`.
- **Regenerated:** `curriculum_v2/cert/alignment.json` and `CERT_COVERAGE.md` were already current after the merge.
- **Targeted tests:** 55 passed (rationales, pass-14 checks, spot-check round 2, cert alignment, adaptive UI and
  e2e fixes). The full suites ran at the end of pass 15; see REFINEMENT_NOTES.
- **Worktree:** `content-wt` was not touched.

## Round 4 (pass 16, Oct 18 2026): misconception tags round 3 (6cabe39)

`content` had last taken `refinement` at `f9ffdc4` (pass 15 rationales and option parity), in `115b85b`. Since then,
`content` added the following, merged locally with nothing pushed:

- misconception tags round 3 (`curriculum_v2/misconceptions_round3.py`): Tests A/B/C items tagged went from 30 to 129
  of 129, and chapter-check items from 183 to 198 of 200. That is 91 `MC-R3` entries, each with a primary source and
  *Pending SME review*;
- `tools/misconception_coverage.py`, with before/after reports in `docs/readiness/`;
- a status line on the mix-up review page.

`refinement` had moved on to `afc0ca4` (pass 15 cert gap items, readiness, notes).

- **Conflicts:** none.
- **Shared file checked by hand:** in `curriculum_v2/misconceptions.py`, the round-3 merge sits after the cert merge
  and before the pass-15 parity tag move. Content wrote its tags against `f9ffdc4`, which already showed the
  rewritten distractors, so they point at the text students see.
- **Targeted tests:** 99 passed (round-3, pass-13/14/15 misconception and check tests, cert alignment, mastery).
- **Worktree:** `content-wt` was not touched.
