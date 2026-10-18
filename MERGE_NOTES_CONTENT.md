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
