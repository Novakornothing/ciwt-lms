# CIWT LMS: refinement notes (branch `refinement`, 2026-10-17)

All of this work is local. Nothing was pushed or sent anywhere.

## 1. Architecture map (what was here)

| Area | Where | Notes |
|---|---|---|
| App | `app.py` (~6.8k lines) | Flask + Flask-SQLAlchemy (SQLite `ciwt_lms.db`) + Flask-Login. `init_db()` seeds the DB when it is imported. |
| Roles | `User.role` admin / instructor / student | An admin can "view as" an instructor (`acting_role`). Access checks go through `role_required` and `instructor_can_access_section`. |
| Curriculum | `lessons.py`, `block*_*.py`, `curriculum_depth.py`, … | `sync_curriculum()` runs on every boot. |
| Assessment | `Quiz`/`QuizAttempt` (no section), `KnowledgeTest`/`TestAttempt` (per section), `compute_item_analysis`, `/analysis/test/<id>`, `instructor_test_performance` | |
| Helix (before) | Models and routes inline in `app.py`, `static/js/helix-gaze.js` (388 lines), `templates/instructor_attention*.html`, `templates/helix_policy.html` | 9-point click calibration with a **hard-coded score of 80**. No validation, no smoothing, no retries. Data was posted only on unload. The dashboard was not linked from the section page. |
| UI | `templates/base.html` held ~1,700 lines of inline CSS. `staff_sidebar.html` is the left rail. | Bootstrap 5.3 CDN + bootstrap-icons |
| Zips in repo root / `/workspace/ciwt/zips/*` | I unzipped and diffed them. | **Every zip is older than `main`.** Each one is a subset of templates and modules already merged, so none were merged. `app 2.py` is also an older copy. Both were left untouched. |

### New layout

```
helix/                 Blueprint "helix": all endpoints are helix.*
  __init__.py          init_app(app, db, deps), seed_demo, context processor
  models.py            define_models(db): sessions, AOI buckets, consent, section settings, additive migrations
  analytics.py         pure functions (breakdowns, summaries, rollups, matrix, heat, lanes)
  routes.py            JSON API + student and instructor pages + CSV
  seed.py              deterministic demo sessions (is_demo=True, labelled in every view)
gradebook.py           GradebookSetting, GradeOverride, compute(), routes (registered via add_url_rule)
static/js/helix/       helix-core.js (pure, UMD, unit tested) · helix-gaze.js (runtime) · helix-charts.js (SVG/canvas)
static/css/            ciwt-theme.css (legacy CSS extracted verbatim) · ciwt-ui.css (tokens/components/mobile) · helix.css
templates/helix/, templates/gradebook/
tests/                 pytest (Flask test client, throwaway DB) + tests/js (node --test)
tools/                 shots.py (Playwright screenshots + overflow check) · helix_e2e.py (browser e2e of the runtime)
```

`python app.py` runs the module as `__main__`. To avoid circular imports, the new modules receive `db` and their dependencies by injection (`define_models(db)` and `init_app(app, db, deps)`) instead of using `from app import db`.

## 2. Changes by priority

### P1: Helix eye-tracking / attention
- **Calibration:** 9 points × 5 clicks, keyboard accessible (Tab + Space; Esc cancels). It is followed by a **5-point validation** that measures median error and precision and computes a real accuracy score: `100·(1 − err/(0.3·diag))·coverage`, banded Good ≥70, Fair ≥45, otherwise Poor. Targets and estimates are drawn on screen. The student gets Retry or Continue anyway; after two failed attempts Helix offers the reading signal. When no gaze estimates arrive at all, the message says so ("No gaze estimates received") rather than reporting 0 px. Instructions and the camera preview sit between target rows, and the preview lets clicks through. Both were added after the browser e2e caught the preview blocking a dot.
- **Smoothing:** WebGazer's own Kalman filter is replaced by `GazeFilter`. It applies a median outlier gate with saccade confirmation (a real jump is accepted after consecutive samples), then a 1-D Kalman per axis, then bounds clamping. `AoiDebouncer` adds hysteresis so fixations don't flicker between headings.
- **State handling:** a 250 ms state machine tracks reading, off page / chrome, face lost, tab hidden, low confidence, idle and paused.
  - Face lost shows a toast after 8 s.
  - A low-confidence streak prompts recalibration, and so does drift after 12 min.
  - The session ends automatically after 15 min hidden.
  - These states count as data-quality time, never as "reading".
- **AOIs:** every heading in `#lessonBody` is an area of interest. The client stores a page layout snapshot (relative y-ranges), a 20×60 heat grid, and debounced segments (a timeline capped at 1,500 segments).
- **Lifecycle and uploads:**
  - `session/start` is idempotent on `client_uuid`, so a retried start does not create a duplicate.
  - The `BatchQueue` uploads every 5 s with sequence numbers and exponential backoff, and persists to localStorage. Leftover queues from a crashed tab are flushed on the next visit.
  - `sendBeacon` sends the final batch on `pagehide`.
  - The server dedupes by `seq`. Cumulative buckets use `max()` so a stale retry can't lower them. Ending is explicit, sessions idle for 10 min are swept to "abandoned", and a returning session is un-abandoned.
- **Models:** `HelixGazeSession` gains mode, device, validation error and precision, recalibrations, per-state ms, rejected samples, last_seq, heat, layout and is_demo. `HelixAoiBucket` gains aoi_kind. New tables: `HelixConsent` (versioned and revocable, with camera and passive scopes) and `HelixSectionSetting` (enabled, passive allowed, min accuracy). Existing DBs are upgraded by additive `ALTER TABLE` migrations.
- **Instructor dashboards:**
  - `/instructor/section/<id>/attention`: KPIs, a signal-quality mix bar, a per-student table (accuracy band, time split, flags), lessons with thin headings, class dwell by heading, a student × heading heatmap matrix (`?lesson=`), per-section settings, and two CSVs (`attention.csv`, `attention-sessions.csv`).
  - Per-student page: SVG AOI timeline swimlanes per session.
  - Per-lesson page: canvas page heatmap with heading markers, dwell by heading, every session's timeline, and the matrix.
  - The dashboard is linked from the section page, the rail and the mobile tab bar.
- **Consent and policy:** a rewritten `/policy/attention` (versioned 2026-10-17) and a `/helix/consent` page to grant or revoke with scopes. The student page `/student/attention` lists sessions and supports per-session or full deletion. The API refuses to record without consent (403 `consent_required`), outside the consent's scope (`consent_scope`), for students not enrolled (`not_enrolled`), or when the section has Helix turned off. The dashboards state on every page that the signal is not an assessment.
- **Mobile fallback:** phones get the passive "reading signal" only, with no camera. It records the block on a reading line at 38 % of the viewport, scroll and touch activity, an idle timeout, and visibility. Passive sessions are labelled separately everywhere.
- **Demo data:** `helix.seed_demo` creates deterministic sessions flagged `is_demo`, and each view that includes them shows an "Includes demo seed data" ribbon. Set `HELIX_DEMO_SEED=0` to disable it.
- **Fix in `app.py`:** `sync_curriculum()` used to delete and re-insert every lesson on boot. That changed lesson ids and orphaned Helix and progress rows. It now updates rows in place, matched on (module, order).

### P2: Mobile responsiveness
- Fixed the root layout bug: `main` had `margin-left: 260px` plus `width: 100%`, so every desktop page was 1,700 px wide. On phones it could also stretch to its widest child. `main` is now explicitly `100% − rail` on desktop and `100%` below 992 px.
- Mobile shell: a drawer for the rail (scrim, Esc to close, focus management) and a bottom tab bar per role (student: Home / Class / Grades / Labs / Menu; staff: Home / Grades / Attention / Messages / Menu). The teaching timer collapses into a toggle with a mini clock.
- Tables are auto-wrapped for horizontal scroll. Tables marked `.table-stack` turn into labelled cards on phones, and mixed cell content is wrapped so each label/value stays on one row.
- Every page in `tools/shots.py` (57 shots: 19 pages × 390×844, 820×1180 and 1440×900) returns 200 with no horizontal overflow. The checker scans every element in `main`, because `overflow-x: clip` hides `scrollWidth`.

### P3: UI/UX polish and accessibility
- `ciwt-ui.css` adds design tokens (surface, ink, brand, radius, type scale) and components: eyebrow, KPI cards, callouts, empty states, checklists, chips, rings, bars and print rules.
- Accessibility:
  - visible focus rings, plus 44 px touch targets on coarse pointers
  - a skip link and `aria-*` on the drawer, theme toggle and flash messages
  - labelled form controls
  - `role="status"` live regions in Helix
  - contrast fixes for the timer, search box and switches on dark headers

### P4: Gradebook
- **Instructor:** `/instructor/section/<id>/gradebook` shows:
  - KPIs (mean, median, SD, % at or above pass, below-pass count, completion) and a grade distribution histogram
  - category averages against weights
  - settings: weights for tests / skills / quizzes (renormalised when a category has no data), best or latest attempt, and pass mark
  - a sticky grade grid with filter, a "below pass only" switch and a quiz toggle; each column shows its mean and pass rate and links to **perf** (section test performance) and **items** (item analysis)
  - cells that link to the attempt detail
  - CSV export (`gradebook.csv`, which includes a class mean row)
- **Overrides:** per student and item, a score or "excused". A note is required and every override is audited.
- **Student:** `/student/grades` (all sections) and `/student/section/<id>/grades`: a grade ring, letter grade, status, per-item attempts and best/last score, and buttons to take open tests.
- Built only on the existing `TestAttempt`, `QuizAttempt` and skills-exam data. It never uses Helix data.

## 3. How to run and test

```bash
./start_lms.sh                       # creates venv, installs deps, serves on :5050 (PORT to override)
# or: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && ./venv/bin/python app.py
```
Demo logins: `admin@lms.local / admin123`, `instructor@lms.local / teach123`, `student1@lms.local / student123`.

Tests and tools:
```bash
./venv/bin/pip install -r requirements-dev.txt && ./venv/bin/playwright install chromium
./venv/bin/python -m pytest -q tests      # 39 tests: per-role 200s, Helix API, gradebook, analytics
node --test tests/js/                     # 10 tests: helix-core filters, validation, debounce, queue
./venv/bin/python smoke_test.py           # public routes
./venv/bin/python tools/shots.py <outdir> http://127.0.0.1:5050      # screenshots + overflow check
./venv/bin/python tools/helix_e2e.py http://127.0.0.1:5050 <outdir>  # real-browser Helix run (passive + camera UI)
```
Each pytest run seeds a throwaway SQLite DB through `DATABASE_URL` and never touches `ciwt_lms.db`.

## 4. Remaining issues and next-pass ideas
- **No CSRF protection** on any POST form, which is pre-existing app-wide. Add Flask-WTF `CSRFProtect` and exempt the beacon endpoint by token.
- WebGazer accuracy is limited: it is realistically about 100–200 px under good light. The dashboards therefore work at heading level and show accuracy bands. Line-level claims would not be honest.
- `datetime.utcnow()` and `Query.get()` deprecation warnings across `app.py`.
- `app 2.py`, `tqi(1).html` and the root zips are stale duplicates. They were left in place because the brief says not to delete user content; review and remove them by hand.
- The gradebook has no letter-scale editor or late-penalty rules yet. Quizzes have no section, so quiz columns count attempts from any section.
- Helix: a real-camera validation was only exercised with Chromium's fake camera, so it still needs testing on a real laptop. Also possible: a per-heading "reteach" export, and showing students their own heat map.
- Very large classes would benefit from pagination of the per-student table and from server-side aggregation caching.
