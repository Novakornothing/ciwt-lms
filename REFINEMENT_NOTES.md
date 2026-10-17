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

## 2b. Pass 3 (2026-10-17): real camera gaze, CSRF, gradebook rules, a11y, deprecations

Commits on `refinement`: `d3f28dd` CSRF · `2bda572` MediaPipe camera pipeline · `dfd8096` deprecations · `9aef0d3` a11y ·
`288f574` gradebook · `0603182` Helix recap/dashboard/report · plus a final commit (results, mobile check, notes, Try-page grid fix, `FLASK_DEBUG` toggle).

### Camera gaze (top priority)
- **Engine** (`static/js/helix/helix-engine.js`):
  - MediaPipe Face Landmarker (tasks-vision 1.1.1, float16 v1 model), **self-hosted** in `static/vendor/mediapipe/`: bundle, WASM and the 3.7 MB `face_landmarker.task`. No CDN at runtime.
  - Runs in VIDEO mode on 1 face, with iris landmarks, the facial transformation matrix (head pose) and blendshapes.
  - Delegate: GPU first, then CPU. `?delegate=CPU` forces CPU.
  - Frame-rate throttle via `requestVideoFrameCallback` with an adaptive target: 15 fps cap on mobile, and it backs off while inference is slow.
  - Falls back to WebGazer if MediaPipe fails to load. If the camera is denied or unavailable, it falls back to the no-camera reading signal.
- **Model** (`helix-model.js`): eye features (iris offset in the eye frame, lid openness, gaze-aware blink) plus head pose (yaw/pitch/roll, distance from iris size). These feed a hybrid model: a geometric gaze-ray projection, then a per-user affine ridge, then a residual ridge. It is trained on calibration and **implicit samples** (click, tap and caret focus within a gate radius), adapts online, keeps **one model per orientation**, and logs drift with a `DriftTracker`.
- **Calibration** (`helix-calib.js`):
  1. Positioning guidance checks distance, centring, facing, level head, eyes visible and light.
  2. A 9-dot calibration (click or **tap** on touch devices); 5 dots for a quick recal after rotation.
  3. A 5-dot validation reports median error in **px and degrees** (96 CSS px/in and the camera's distance estimate), plus precision and band.
  - **AOI resolution adapts** to the error: heading → paragraph → line.
- **Mobile:**
  - front camera (`facingMode: 'user'`), `playsinline`/`webkit-playsinline`/muted video
  - portrait coordinate mapping and a separate model per orientation: rotating to an orientation that hasn't been calibrated runs a quick 5-dot calibration; rotating back reuses the stored model
  - phone distance band, battery/heat throttling
- **Live preview / debug:**
  - `/helix/try` is public and stores nothing. It shows a gaze dot, gaze-target tiles, implicit click-to-teach, a drift chart and a diagnostics HUD (engine, delegate, fps, inference ms, face %, distance, yaw/pitch, samples).
  - The lesson dock has a "Debug" HUD toggle and the gaze dot.
- **Server:** sessions store engine, delegate, validation °, distance, AOI resolution, orientation, implicit sample count, a drift series, and fine (paragraph/line) dwell. **No landmarks or video are ever stored.** Instructor student pages show the drift sparkline.
- **Measurement:** see `tools/helix_eval/RESULTS.md`; the summary follows.
  - The synthetic harness (`node tools/helix_eval/eval.js --users 20`) is deterministic.
    - Baseline: **1.63° median (75 px)**. Low noise: 0.69°. High noise: 4.03°. Phone geometry: 0.88°.
    - Head moved 4 cm + 5° after calibration: 4.09°, then 1.88° after 20 implicit clicks. A single-ridge ablation scored 9.2° on the same test.
  - Real-face fake camera (CC0 clip as y4m via `--use-file-for-fake-video-capture`): real MediaPipe on CPU ran at 22–27 ms/frame, found a face in 100% of frames, and gave moving estimates at 10–13 fps on desktop and phone emulation. All API calls returned 200 with CSRF on, and sessions were stored with metadata. The validation "error" (16–20°) is **not accuracy**: the person in the clip isn't looking at the dots.
  - Replay of 401 recorded frames found that the old blink rule discarded 28% of frames (the person was looking down, not blinking). The fixed rule discards 1%.
  - **No real person on a real device has been measured yet.** The first live validation will give that number.

### Other pass-3 items
- **CSRF:**
  - Flask-WTF `CSRFProtect` covers every form; fetch POSTs send an `X-CSRFToken` header.
  - Helix `sendBeacon` sends the token in the body, and the server validates it.
  - Bearer-token APIs are exempt.
  - Tests cover rejection and acceptance.
- **Helix extras:**
  - an encouraging student **reading recap** after each session, with jump links to thin sections and no judgmental wording
  - an SQL-aggregated, paginated attention dashboard. On a 300-student bench: 345 ms/1.3 MB → about 90–140 ms/250 KB.
  - a printable/PDF **attention report** (`/instructor/section/<id>/attention/report`)
- **Gradebook:**
  - `QuizAttempt.section_id` is set when a quiz is taken. Older attempts are included only if they fall inside the student's enrollment window, and the excluded ones are counted.
  - a letter-scale editor (validated JSON scale)
  - late penalties: % per day, a cap, grace hours, and per-item due dates. The grid shows an "L" marker with a tooltip, and the CSV includes the penalty.
  - signature-checked result cache, invalidated on every write
  - server-side filter and pagination
  - fixed a gold-path crash on modules that have labs
- **Accessibility:**
  - `tools/a11y_sweep.py` runs axe-core (WCAG 2.1 AA) over 57 page/width combinations: 294 → **0 violations**
  - fixes: contrast tokens, labels on selects and inputs, keyboard-focusable scroll regions, icon roles
  - Try-page tile grid no longer overflows at 390 px
- **Deprecations:** `datetime.utcnow()` → `utcnow()` helper; `Query.get()`/`get_or_404` → `db.session.get`/`db.get_or_404`. pytest runs with 0 warnings.
- `app.py` honours `FLASK_DEBUG=0`. The default is unchanged (debug on); turn it off whenever the app is exposed through a tunnel.

## 3. How to run and test

```bash
./start_lms.sh                       # creates venv, installs deps, serves on :5050 (PORT to override)
# or: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt && ./venv/bin/python app.py
```
Demo logins: `admin@lms.local / admin123`, `instructor@lms.local / teach123`, `student1@lms.local / student123`.

Tests and tools:
```bash
./venv/bin/pip install -r requirements-dev.txt && ./venv/bin/playwright install chromium
./venv/bin/python -m pytest -q tests      # 59 tests: per-role 200s, CSRF, Helix API/engine meta/recap/report, gradebook rules
node --test tests/js/                     # 20 tests: helix-core + helix-model (features, blink, regressor, orientation, drift)
./venv/bin/python smoke_test.py           # public routes
./venv/bin/python tools/shots.py <outdir> http://127.0.0.1:5050      # screenshots + overflow check
./venv/bin/python tools/helix_e2e.py http://127.0.0.1:5050 <outdir>  # real-browser Helix run (passive + camera UI)
./venv/bin/python tools/a11y_sweep.py                                  # axe-core WCAG 2.1 AA sweep
node tools/helix_eval/eval.js --users 20 --json tools/helix_eval/results.json   # synthetic gaze accuracy
node tools/helix_eval/replay.js --json tools/helix_eval/replay_results.json     # recorded-landmark replay
# real MediaPipe with a face video as the camera (y4m):
./venv/bin/python tools/helix_mp_e2e.py http://127.0.0.1:5050 face.y4m <outdir> --delegate CPU [--mobile --viewport 390x844 --tag mobile]
./venv/bin/python tools/helix_lesson_e2e.py http://127.0.0.1:5050 face.y4m <outdir> --db ciwt_lms.db [--mobile --viewport 390x844 --tag mobile]
./venv/bin/python tools/helix_mobile_check.py http://127.0.0.1:5050 face.y4m <outdir>   # front cam, playsinline, taps, rotation
```

### Testing camera gaze on a real laptop and phone
- **Laptop:** run `./start_lms.sh` and open `http://localhost:5050/helix/try`. Browsers treat localhost as a secure context.
  1. Click **Start camera & calibrate** and allow the camera.
  2. Follow the positioning checks, then click each of the 9 dots while looking at it.
  3. Look at the 5 validation dots and read the px/° error.
  4. Look at the tiles. Click a tile while looking at it to teach the model, and watch the drift chart drop.
  - For a lesson, log in as `student1@lms.local / student123`, open a lesson, choose camera in the Helix dock, and use "Debug" to see the HUD.
- **Phone (needs HTTPS):**
  1. On this machine, start the app with the debugger off: `FLASK_DEBUG=0 ./start_lms.sh`.
  2. Start a tunnel: `/workspace/ciwt/bin/cloudflared tunnel --no-autoupdate --url http://localhost:5050`.
  3. Open the printed `https://<random>.trycloudflare.com/helix/try` on the phone, with the phone at about 30 cm and at eye level.
  4. Tap **Start**, allow the camera, then tap each dot while looking at it.
  5. Rotate the phone and do the quick 5-dot recal; rotate back and check that the portrait model is reused.
  - Stop the tunnel with Ctrl-C. The URL is public while it runs, so share it only with testers.
Each pytest run seeds a throwaway SQLite DB through `DATABASE_URL` and never touches `ciwt_lms.db`.

## 4. Remaining issues and next-pass ideas
- **Real-device accuracy is unmeasured.** Every camera number so far comes from synthetic landmarks or from a recorded face that isn't looking at the targets. The first real sessions must be checked against the validation readout. The synthetic 1.6–4° figures are a model-level estimate, not a promise.
- **Untested on real hardware:**
  - iOS Safari and Android Chrome: permission prompts, `orientationchange` timing, the WebGL GPU delegate, thermal throttling
  - real GPUs. SwiftShader "GPU" here was 100+ ms/frame, so the e2e runs force CPU.
  - glasses, low light, varied skin tones, multiple faces
- Paragraph AOIs need validation error ≤ 0.6 × paragraph height (about 66 px), and line AOIs ≤ 0.75 × line height (about 20 px). Expect heading level on most webcams.
- The local dev DB `ciwt_lms.db` now holds e2e sessions (students 12 and 13, sessions ~31–36, engine `mediapipe`), created by the fake-camera runs. They are real rows, not demo seed data. Delete them from `/student/attention` as those students if you want a clean demo.
- `app 2.py`, `tqi(1).html` and the root zips are stale duplicates. They were left in place because the brief says not to delete user content; review and remove them by hand.
- WebGazer is still vendored as a fallback (large). It could be dropped once MediaPipe is proven on target devices.
