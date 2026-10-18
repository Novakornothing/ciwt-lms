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
- `app.py` honours `FLASK_DEBUG`. Since pass 10 the default is **off**; `FLASK_DEBUG=1` turns it on and binds to 127.0.0.1.

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
  1. On this machine, start the app: `./start_lms.sh` (the debugger is off by default since pass 10; never set `FLASK_DEBUG=1` behind a tunnel).
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

---

## Pass 4 (Oct 17 2026): real-world robustness, calibration UX, privacy, entry page, polish

Local branch `refinement` only; nothing pushed, no tunnel, no curriculum removed.

### Public entry + product name
* **Name: "Novak Learning"**, tagline "Info Systems Training". Both live in one place:
  `SITE_NAME` / `SITE_TAGLINE` at the top of `app.py` (or the `SITE_NAME` / `SITE_TAGLINE` env
  vars), exposed to templates as `site_name` / `site_tagline`. They appear in every `<title>`
  (all templates now end "— {{ site_name }}"), the header wordmark, the footer, the role
  picker, the sign-in page and the Helix report footer. `site_email_subject()` is the hook for
  emails; the app sends no email today (messages are in-app only).
* `/` (signed out) is now a role picker with three large cards: **Learn** (students),
  **Teach** (instructors), **Admin** (administrators). Each card has a one-line description and
  links to `/start/<learn|teach|admin>`, which sends signed-in users to their own home and
  everyone else to `/login?as=<role>`. Sign-in shows a segmented role switcher and a role
  heading; demo accounts sit in a collapsed "Demo accounts" panel. The account's real role
  always decides where you land. The "CIWT LMS" wordmark is gone from header, title and footer.
  The repo, Python identifiers and curriculum text were not renamed.

### Eye tracking robustness (helix-model.js / helix-engine.js / helix-gaze.js)
* Accuracy proxy on real faces through the real MediaPipe path: tools/helix_eval/warp/*,
  results and caveats in tools/helix_eval/RESULTS.md ("Pass 4").
* Light and glare: brightness/contrast measured on the **face box** (backlight shows as low
  contrast) and glare in the eye regions. Positioning checks now say "Face too dark",
  "over-exposed", "backlit?" or "Glare on glasses", and ask the camera for continuous
  exposure / white balance when it is dark. Sustained darkness, glare or occlusion while
  reading triggers a one-time tip.
* Multiple faces: `numFaces: 2` plus `_pickFace` locks onto the calibrated person (falls back to
  the largest face), with a one-time "another face is in view" note.
* Partial occlusion: frames where one eye departs from its calibration shape, or the iris
  leaves the eye, are dropped.
* Blinks: `BlinkGate` compares openness with the person's own recent baseline. Short closures
  are blinks; sustained narrowing (looking down) is kept.
* Fixations: `detectFixations` (I-DT / I-VT) and an online `FixationDetector`. Lesson AOI dwell
  follows the current fixation; saccades/outliers keep the previous block, with a 600 ms
  fallback to smoothed samples so dwell never freezes on noisy setups.
* Smart recalibration: pose snapshot at calibration vs a 4 s window (distance ratio, yaw/pitch
  9°, face shift). It prompts only after ~6 s of sustained change.
* Viewport: Android top-bar shift compensation; resize keeps filters in bounds.
* Mobile: camera opened **inside the tap** (`prefetchCamera`, iOS gesture rule), with the
  prefetched stream released if WebGazer takes over. `play_blocked` gives a "Tap to start
  camera" button. Load failures name memory limits. WASM SIMD is probed and reported.
  Thermal back-off cuts fps to 60 % when inference slows 1.7x; low battery caps it at 10 fps,
  without undoing thermal. Debug HUD shows faces, light, glare, occlusion, power, SIMD and
  camera resolution.
* Bug fixed: `fitPursuit` compared lags on different row sets, biasing toward the longest lag.

### Calibration UX (helix-calib.js)
* Choice on the positioning screen: **Tap 9 dots** (default, "most reliable") or **Follow a
  moving dot** (9 s Lissajous + 3 anchor dots, no clicking). Follow falls back to dots
  automatically if the face was lost.
* Progress bar across all three steps (role=progressbar with value text), encouraging copy
  ("Nice.", "Halfway there.", "Last one!"), shorter dot hold (0.9 s), friendlier failure text.
* Time-to-calibrate measured: `score.calibMs` (first dot -> end of check), `score.totalMs`
  (with positioning) and `score.calibMode`, shown on the result card. Automated e2e with the
  CC0 face video: **23.5 s for dots and 23.5 s for follow**, including the ~8 s accuracy check
  and robot pacing (1.35 s per dot). Not a human measurement.

### Privacy
* Server: a blueprint `before_request` on `/api/helix/*` refuses (400 `media_not_accepted`)
  any body with image/video/landmark keys, `data:`/`blob:` URLs or long base64 strings, and
  bodies over 256 KB (413). This runs before any session lookup.
* E2E audit (tools/helix_lesson_e2e.py) records every request during a real camera session.
  Result: 5 Helix uploads, 11.2-11.5 KB total, largest 6.7 KB, no media-like content, no
  off-site posts, and the forged frame upload is refused with 400. **pass: true.**
* Policy page has a new "What leaves your device (and what never does)" section; the
  calibration, blink, fixation and battery behaviour is documented there too.

### UX polish (weakest 8 things, from critical screenshot review)
1. Student home: the generic "Your training" banner repeated the gold-path text. It is now a
   greeting with a progress meter ("3 of 4 steps done") and the **Continue** button above the
   fold on phones.
2. Gold path: a graded test already taken but now closed read "closed until an instructor
   opens it" next to a check mark. It now shows "your score NN%".
3. Gold path step details were #8aa0b8 on white (2.6:1); now the AA ink-muted colour. The
   check mark has a screen-reader "Done:" label.
4. Lesson reader (phone): five hero buttons plus a two-row narration bar pushed the lesson
   below the fold. Now there are two hero buttons, text links for All lessons / Report an
   issue, and a one-row Listen bar with options behind "⋯". The native audio player is hidden
   until playback starts.
5. Lesson reader: removed the duplicate Full screen button (the content-header one remains).
6. Lesson reader (desktop): the Helix card auto-opened over the lesson text; it now starts as
   the small pill.
7. Instructor class page: "Run class" sat below two duplicated lists (skills tests, chapter
   list). The tabs now follow the hero (sticky), with a live status ("2 tests open now",
   "13 of 13 chapters unlocked"). Hero links switch tabs; the broken `#roster` / `#chapters`
   anchors are fixed.
8. Instructor: Open/Closed and Locked/Unlocked use icon + text (not colour alone), "until —"
   reads "with no end time", and the tabs have proper tab roles.

### Tests
* pytest: 63 passed (new: media guard, size limit, entry page, signed-in redirect).
* node: 24 passed (new: I-DT/I-VT, FixationDetector, BlinkGate, fitPursuit lag, recalTrigger).
* axe-core 4 (WCAG 2.0/2.1 A+AA): 22 pages x 3 widths = 63 checks, **0 violations**.
* Synthetic regression: unchanged (4 cm/5° drift 4.09° -> 1.88° after 20 clicks).

### Still untested on real devices
Real iOS Safari (gesture/playsinline/low-power play block, memory on older iPhones), real
Android low-end throttling and thermal behaviour, real glasses glare and room lighting,
exposure constraints (support varies by camera), a real second person in view, and accuracy
with real people looking at a real screen.

---

## Pass 5 (Oct 17 2026): high-resolution eye crop, A/B'd on the warp proxy

Local branch `refinement` only; nothing pushed, no tunnel. Full numbers:
tools/helix_eval/RESULTS.md ("Pass 5") and tools/helix_eval/warp/RESULTS_v5.md.

**Outcome (honest):** the crop features give small average gains on 9-point calibration (best
-0.45° mean over 55 sequences). **None was consistent across all subjects and both seeds**, and the
ported version made follow-the-dot calibration slightly worse. Following the acceptance rule,
**the default gaze model is unchanged from pass 4**. Everything new is behind flags.

### Kept (on by default)
* Second-stage eye crop in **view-only** mode on the Try page: the "Live diagnostics" card shows
  both pose-normalised full-resolution eye crops with the lid contour, the gradient (Timm & Barth)
  pupil centre and the dark-centroid estimate. It costs 2-4 ms/frame on desktop CPU and doesn't
  touch the model. HUD rows "Camera" and "Eye-crop stage" were added (the lesson debug dock shows
  "Eye crop" too).
* Engine guard: crops are cleared when the face is lost; the stage switches itself off below ~12 fps.
* `ridgeFit` treats missing feature values as the mean (needed by the flagged paths; no effect on
  23-dim vecs).
* Eval tooling: warp seeds and a 1080p source (`gen.py --seed`, cbp1080), bench dumps of crop
  features, `crop_ab.js` (feature-group / lambda A/B with paired statistics), `CROPVEC` in
  `warp_eval.js`, and an HUD screenshot step in `helix_mp_e2e.py`.

### Behind flags (built, measured, not default)
* `crop: true` (engine option; Try page `?crop=1`) appends 8 crop features (pupil x/y per eye,
  upper/lower lid per eye) to vec. `GazeRegressor` then uses them in stage 2 with grouped-CV
  lambda. All 55: 7.53 → 7.19° median (mean -0.22°, CI includes 0). It is worse on 640x480 cbp
  (7.53 → 8.48°) and on follow-the-dot + 3 dots (+0.20°).
* `hiRes` (`window.HELIX_ENGINE.hiRes` or `?hires=1`): requests 1920x1080 on desktops with ≥8
  cores and falls back to 720p at runtime if inference + crop exceeds 50 ms. Same person and frames:
  follow-the-dot + 3 dots 6.22 → 5.28° (9/10 pairs), 9-point mixed (7/11). Only one subject has a
  1080p source, and inference rises from 29 to 40 ms/frame.
* `detectWidth` (engine option): runs face detection on a downscaled copy (1080p: 39.9 → 36.3 ms).
  Accuracy not A/B'd.

### Rejected (offline only, not ported)
* Eye-appearance patches (15x9 → 10x6 PCA-12 or 5x3, rank-equalised, pose-normalised): the
  biggest average gain (-0.37 to -0.45°, p=0.014), but cbp and cbp1080 got worse over their 7
  conditions. That is not consistent, and there is no vertical gain.
* Grouped-CV lambda on its own (no crop features): -0.21° mean, 30/55 wins, 3/5 subjects.
* Per-user feature-group selection by CV: -0.35° mean, but 3/5 subjects on the 7-condition set.
* Dark-centroid pupil instead of Timm & Barth: weaker everywhere (it stays as the fallback, and
  as the cheap phone option at 0.7 ms).

### Why the ceiling barely moved
At 640x480/720p the eye crop upsamples (0.34-0.72 camera px per crop px). MediaPipe already sees
the eyes at roughly native resolution, so the crop adds an estimator, not information. The error
on this proxy is dominated by head-pose-related scatter, not by pupil localisation. The warp moves
lids but has no eyeball shading or corneal reflection, so a real-eye test could rank the
appearance features differently.

### Tests
* `tests/js/helix-crop.test.js` (7 tests) covers: crop transform (level, centred, scale), Timm &
  Barth / centroid on a synthetic eye (<1.5 / <2.5 px), pupil shift and lid aperture, patch
  equalisation, `cropVec` NaN handling, crop-aware regressor (grouped CV chosen, vertical error
  halved on synthetic data), missing-value equivalence, and `cvGroups`.
* Results: node 31/31, pytest 63 passed, axe 63 pages with 0 violations, fake-camera Try-page
  e2e (1280x720) OK.
* Screenshots: /workspace/ciwt/screenshots/pass5/try-hud-eye-crops.png and try-live.png.

## Pass 6 (Oct 17 2026): full-site UI/UX and mobile polish

Scope: every route for every role. Each page was screenshotted at 390/820/1280 in light and dark (`tools/site_audit.py`), critiqued and fixed over two rounds. Helix accuracy work is paused. Everything is local; the real DB was snapshotted and left unchanged (screenshots and e2e ran on a copy).

### Changes by area
- **Quizzes and tests:** one shared runner (`static/js/assessment.js` + `templates/_assessment.html`; quiz.html and test.html are now thin wrappers). On phones it runs in focus mode: tab bar and footer hidden, a fixed action bar at the bottom, and a sticky toolbar with the timer (turns amber at 10 min and 5 min, red in the last minute, auto-submits as "Time expired"). Answers survive a reload (sessionStorage) and are cleared on submit. The review modal has jump chips. Options are keyboard-reachable (the old radios used `display:none`), with ←/→/F shortcuts, aria-current/aria-pressed states and textContent-only rendering. `tools/assess_phone_e2e.py` runs the flow end to end on a phone (39 checks).
- **Results:** 3-up KPI row, pass/fail hero, skill meters, focus areas sorted by most missed (first 3 shown, the rest collapsed) with wrapping lesson chips, and Try again / See my grades actions.
- **Student class page:** progress meter, full-width actions on phones, chapter labs in a disclosure, Skills tests no longer listed twice, friendly empty states (developer "Render deploy" text removed), critique form collapsed.
- **Labs:** one `lab_row` component. Course labs are grouped by chapter with jump chips, and the skill map is collapsed and shows lab titles. The live lab terminal no longer overflows phones (grid `minmax(0,1fr)`); the input has autocorrect off and no autofocus on touch.
- **Gradebook and grades:** 44 px touch chips, names and sort headers; grade rows stack compactly on phones.
- **Instructor analytics:** test performance and item analysis use a `kpi-grid` (3-up on phones) plus summary pills instead of a wall of metadata.
- **Navigation:** the mobile Menu drawer opened below the page because of a legacy `position: static !important` rule; it now opens on screen. Bug predates pass 6. The rail has Account & settings and Sign out. Root-only breadcrumbs removed.
- **Account:** new `/account` page for every role: profile, theme choice, password change with inline validation (400 on error, flash on success, audited), privacy links.
- **Feedback and empty states:** flash messages with an icon and role per category; shared `empty_state` macro (inbox, search, tickets); `form[data-confirm]` replaces all 7 inline `onsubmit=confirm()` handlers; inbox has a header with an unread badge and CTA; friendly 404/403/500 pages (API 404s stay JSON).
- **Forms:** removed a global `.form-label { white-space: nowrap }` that clipped long labels; 50 labels associated with their fields; check labels fill a 44 px row on touch.
- **Design system:** the `<style>` blocks from the lab and sidebar pages moved into ciwt-ui.css; 41 static inline styles replaced by `u-*` utilities. Touch overrides sit after the component blocks so they win the cascade.
- **Performance:** fonts and bootstrap-icons load non-blocking (preload + noscript); Mono weights trimmed to 400/600; preconnect to jsDelivr; 2 KB favicon (was the full logo) and `/favicon.ico` → 301. Versioned static files are served `immutable`, others max-age 86400 (tested).
- **Touch:** quiz Flag/Report, the narration menu, the demo-accounts disclosure, icon-only delete buttons, TQI status links and stacked grade chips are all 44 px on touch.
- **Accessibility:** axe gives 0 violations on 63 page/width combinations (the lab row "Launch" text was darkened in light mode).

### Tests
pytest 73 passed (new: error pages, account flows, caching headers, favicon, no inline confirm); node 31 passed; phone e2e 39/39 in light and dark; axe 0.

### Screenshots
`/workspace/ciwt/screenshots/pass6/`: `before/`, `after/` (light 390/1280), `after-dark/` (390), `phone-e2e-light|dark/`, `pairs/` (side-by-side before | after at 390 px: anon-404, student-quiz, student-class-labs, student-lab, instructor-item-analysis, instructor-test-perf).

### Remaining issues
- Bootstrap CSS from the CDN is still render-blocking. Self-hosting it, or using a critical-CSS split, would help first paint.
- The dev server doesn't gzip; enable compression at the proxy in production.
- `static/img/navy-n.png` (2.1 MB) and `navy-interior-live.webp` (604 KB) are unreferenced. Candidates for removal (left in place).
- Duplicate "… (1).html" templates were left untouched.
- A test POST renders results directly, so reloading the results page offers to resubmit (should be POST-redirect-GET).
- Data-driven inline widths (progress bars, histograms, distractor bars) are intentionally kept inline.
- The admin dashboard is still long; jump chips help, but it should be split into tabs or pages.
- At 390 px the only targets under 44 px are inline text links inside sentences (lesson, module and attention pages), which WCAG 2.5.8 exempts.
- Small-target counts at 1280 are mouse context (no touch rules) and are acceptable.

## Pass 7 (Oct 17 2026): fixes for the issues left after pass 6

Same rules as before: local only, small commits. The real DB was left unchanged; tests and screenshots used a copy.

### 1. Self-hosted assets and compression
- **Self-hosted:** Bootstrap 5.3.3 CSS/JS, Bootstrap Icons 1.11.3 and the IBM Plex Sans/Mono and Orbitron fonts now live in `static/vendor/<package>/<version>/` (licences included).
  - No page requests anything from jsDelivr or Google before first paint. The webgazer CDN fallback is removed too (the local copy was already primary).
- **Fonts:** latin and latin-ext woff2 only. Plex Sans and Orbitron are variable fonts, so each is one file covering all weights. The body font is preloaded with the same URL `fonts.css` uses, so it downloads once.
- **Icon subset:** the full icon set is about 216 KB (font plus CSS); the app uses about 115 icons.
  - `tools/build_icon_subset.py` builds a 10 KB font and 5 KB CSS, with a content hash in the font filename.
  - A test fails if a template uses an icon that isn't in the subset; run the tool again after adding one.
  - `bi-flask` (the demo-data ribbon) never existed in 1.11.3 and now uses `bi-database-gear`.
- **Caching:** `?v=` URLs, plus anything under a version directory in `static/vendor/`, are `immutable` for a year. That covers fonts referenced through `url()` inside vendored CSS.
- **Compression:** Flask-Compress (added to `requirements.txt`). Brotli when the browser accepts it, otherwise gzip; static files stream through the same encoders. Fonts and images are left alone.
  - It runs inside the app, so it works the same under `flask run`, `python app.py` and **gunicorn as started by the Procfile/render.yaml**. Verified locally with `gunicorn app:app`: `/login` 16 KB becomes 5.3 KB (br) or 5.3 KB (gzip), and `bootstrap.min.css` 233 KB becomes 33 KB (br) or 31 KB (gzip). The gzip body decodes back to the identical file.
  - No compressed-response cache is used, because pages are per user.
- **Measurements** (`tools/perf_probe.py`: cold cache, 390 px phone, Lighthouse "slow 4G" 150 ms RTT / 1.6 Mbit/s; JSON in `screenshots/pass7/perf-*.json`):

| Page | Bytes over the wire | First contentful paint | Load | 3rd-party requests |
|---|---|---|---|---|
| login | 482 → 242 KB | 1500 → 1120 ms | 2910 → 1635 ms | 4 → 0 |
| student home | 493 → 245 KB | 1472 → 1116 ms | 2904 → 1635 ms | 4 → 0 |
| student class | 518 → 248 KB | 1584 → 1108 ms | 3067 → 1672 ms | 4 → 0 |
| lesson | 706 → 318 KB | 2104 → 1232 ms | 3857 → 1912 ms | 4 → 0 |
| admin home | 525 → 245 KB | 1600 → 1092 ms | 3059 → 1689 ms | 4 → 0 |

### 2. Post/Redirect/Get
- Quiz, knowledge-test and skills-practical submissions now save the attempt and answer **303** to `/student/quiz/<section>/<quiz>/result/<attempt>` or `/student/test/<section>/<test>/result/<attempt>`.
  - The results page is a plain GET rebuilt from the stored answers. Reloading it, or going Back and then Forward, never resubmits.
  - "Time expired" survives the redirect as a flash plus `?timed_out=1`.
- Only the attempt's owner or staff can open a result; anyone else gets 404. An attempt that is still open sends you back to the test.
- The other POST forms already redirected on success. Login and account re-render only to show validation errors (account returns 400), which is normal PRG practice.
- Tests: `tests/test_prg.py`. The phone e2e now also checks that results have their own URL and that a reload is a GET that adds no attempt (43 checks).

### 3. Admin split
- `/admin` is now a short **overview**: 6 KPI cards that link through, 4 area cards, more-tools chips, the top teaching time and the demo reset.
- The rest moved to sub-pages that share a sub-nav (`templates/_admin_nav.html`):
  - **Classes** `/admin/classes`: sections table that stacks on phones, create form, teaching time.
  - **People** `/admin/people`: user list with role filter chips and name/email search; the add forms collapse.
  - **Curriculum** `/admin/curriculum`: a card per curriculum set with chapters, lessons, quizzes, tests, labs, its classes and course instructors, plus the add form.
  - **Quality / TQI** `/admin/tqi`: the existing board, with the shared header; its inline `<style>` moved to CSS.
- On phones the sub-nav scrolls sideways, keeps the current tab in view and fades the edge.
- **Old bookmarks:** `/admin#admin-class|sections|course-instr|people|staff` forward from `<head>` to the matching sub-page and anchor. Admin form POSTs return to their own sub-page. The staff rail and tab bar know the new pages.
- On a phone the admin home went from 5,223 px to 1,748 px. Tests: `tests/test_admin_pages.py`.

### 4. Archive
- `git mv` (nothing deleted) of `app 2.py`, the four `templates/*(1).html` duplicates, `navy-n.png` (2.1 MB), `navy-interior-live.webp` (604 KB) and 14 stale root zips into `archive/`. Each was grepped first: nothing referenced them.
- `archive/README.md` explains each file and how to restore it. `archive/` is `export-ignore`, so the release zip leaves it out.

### 5. Dark-mode accessibility
- `tools/a11y_sweep.py --themes light,dark` checks 29 pages at 3 widths (now including the admin sub-pages, account, inbox, class labs and grades).
- 65 dark-mode contrast failures fixed:
  - The dark role accents never applied. `[data-theme="dark"][data-role=…]` needed a descendant selector, because `data-theme` is on `<html>` and `data-role` on `<body>`. Instructor (gold) and admin (coral) pages now get their dark-tuned colours.
  - Bootstrap `*-emphasis` text, warning badges with `text-dark`, `btn-outline-danger` and `btn-link` got dark-theme colours.
  - Chip links keep ink text in dark mode.

### Tests
pytest **96 passed** (was 73); node **31 passed**; phone quiz/test e2e **43/43** in light and dark; axe **0 violations** (174 page/width/theme checks).

### Screenshots
`/workspace/ciwt/screenshots/pass7/`:
- `before/` and `after/`: admin pages at 390/1280, light and dark.
- `pairs/`:
  - `admin-390-light-before-vs-after.png`: the old 5,223 px page beside the overview and each sub-page, at the same scale.
  - `admin-390-overview-top.png`: the first screen on a phone.
  - `admin-1280-light-before-vs-after.png`
  - `admin-390-dark-before-vs-after.png`
- `phone-e2e-light|dark/`, `axe/axe-report.json`, `perf-before.json`, `perf-after.json`.

### Left for later
- Five same-origin stylesheets still block render (Bootstrap is 33 KB br). Inlining critical CSS, or merging theme, ui and helix CSS into one file, would cut first paint further.
- `navy-n-512.webp` (60 KB) loads on every page as a CSS background; a smaller variant would save about 50 KB.
- Compression runs per request. That's fine at this scale; at higher traffic, pre-compress static files at build time or let a CDN/proxy compress.
- The People list shows everyone (28 in the demo; 4,629 px on a phone). Add pagination if the user count grows.
- `n74-ops-worker 4.js` in the repo root looks like another stale duplicate. It was outside this pass's list, so it is untouched.
- Small-target counts at 1280 are mouse context (touch rules apply below 1000 px).

---

## Pass 8 (Oct 17 2026): classroom-ready curriculum

The full audit is in **CURRICULUM_AUDIT.md**. The revised content is a layer in `curriculum_v2/`; the original lesson,
bank and pilot text is unchanged in place and in git.

**Assessment and content corrections**
- Item review for all 270 bank and check items (`curriculum_v2/item_review.py`): 226 revised, 173 keys reworded so
  answer length is no longer a cue, 21 stems rewritten, key positions rotated. Each item now has an objective code and
  a rationale.
- Two wrong items fixed: N1.2 had two correct options, and N1.4's key was hedged. A1.13's stem gave the answer away.
- The NETOPS chapter checks were three generic sets rotated across chapters. They are replaced by 56
  chapter-specific items (`netops_checks.py`).
- 30 supplementary exam items cover 15 objectives that had no test item (`exam_supplement.py`). They are kept out of
  the LMS A/B/C forms, so live forms stay stable.
- Labs: three unused labs are now mapped, existing labs are attached to ITSUP 7/11 and NETOPS 5, and four classroom
  labs were written (CL-4/6/9/12).
- Factual updates:
  - Windows 11 25H2 (23H2 service ends 10 Nov 2026)
  - Windows 10 end of support and ESU dates
  - VM hosts and vTPM requirements
  - NIST SP 800-63B-4 password guidance
  - Wi-Fi 4–7, USB-IF naming, DDR5, Cat6 10GBASE-T distance
- Leaks fixed: teaching notes (`.instructor-note`) are stripped server-side for students, and answer keys no longer
  appear in quiz page source.

**Course package (`curriculum_v2/course_package.py`, `documents.py`)**
- Syllabus template with:
  - credit hours (34 CFR 600.2: ITSUP and NETOPS 4 credits, CLIENT 3)
  - CLOs, objectives and grading taken from the section's gradebook settings
  - policy placeholders and an accessibility statement
- Pacing guides for 16, 8 and 10 weeks, and a 150-minute session template.
- Lesson plans for every chapter.
- Lab manual in a standard format (objective, equipment, safety, steps, evidence, rubric).
- Rubrics (lab, skills exam with critical errors, ticket, discussion).
- Midterm and final blueprints with form coverage.
- Answer keys as a separate instructor-only document.
- A glossary of about 60 terms.
- `tools/build_course_package.py` writes DOCX and PDF to `/workspace/artifacts/course-package/<CODE>/` (student-safe
  files) and `<CODE>/instructor-only/`, 44 files in total.

**In the app (`curriculum_v2/materials.py`)**
- `/instructor/materials` lets instructors view, print and download every document (DOCX or PDF).
- `/instructor/section/<id>/syllabus` sets per-section syllabus details (institution, term, meetings, instructor,
  policies, pacing length) in a new `syllabus_settings` table. Grading weights, pass mark and scale come from the
  gradebook settings.
- Students get a Syllabus button on the class page (`/section/<id>/materials/syllabus|pacing|rubrics|glossary`).
  They can reach only student-safe documents, and only for sections they are enrolled in. Unfilled `[placeholders]`
  are flagged.
- Each lab page has a "How this lab is assessed" panel (rubric criteria plus the linked skills-exam station).
- On phones, item/details document tables stack. Document tables wrap: the answer key now fits 927 px, where it was
  3112 px.

**Tests (end of pass)**
- pytest: 157 passed, including `test_curriculum_integrity.py` and `test_materials.py`.
- node: 31 passed.
- Phone e2e: 43/43 in light and 43/43 in dark.
- axe-core: 216 page/width checks with 0 violation nodes in light and dark. The sweep now includes the materials,
  syllabus, rubrics, syllabus-settings and lab pages. After the table CSS change the document pages were re-run
  (42 checks, 0 violations, no overflow).
- Screenshots are in `/workspace/ciwt/screenshots/pass8/`.

**Still open (SME or institution):** see the "Still needs" section of CURRICULUM_AUDIT.md.

## Pass 9 (Oct 17 2026): ITSUP chapters 7–13 expanded (pending SME review)

The full detail is in the “Pass 9” section of **CURRICULUM_AUDIT.md**. The new content is a layer in
`curriculum_v2/itsup_core/`, with one module per chapter (`ch07.py` … `ch13.py`). `apply.py` adds it to each
lesson as a “Lesson objectives” panel and a `Core content` section. The original `lessons.py` text is unchanged.

**What was added**
- **Lessons:** chapters 7–13 now have 3,355–4,643 words each (ch1 has 6,524 and ch2 has 3,493). Every lesson has measurable objectives, at least 300 words of core content and check-for-understanding questions. Every chapter has a worked example, a troubleshooting scenario and a diagram.
- **Diagrams:** 8 inline SVGs, each with role="img", a title/desc, a caption and a text description. Phones get a separate two-column version.
- **Objectives:** 5 new chapter objectives: IT-7.4, 9.4, 11.4, 12.4 and 13.4.
- **Items:** 85 (`X-IT-*`) with rationales.
  - At least 3 per objective.
  - Key positions are 22/21/21/21.
  - The key is the longest option in 22/85 items, counting ties.
  - These items are in the answer key and blueprints only, not in the live Test A/B/C.
- **Glossary:** 64 new terms, marked †.
- **Lesson plans:** for every expanded chapter: warm-up, guided practice, worked examples, CFU, exit ticket, misconceptions, lab.
- **Classroom labs:** 5 new in the standard format with the lab rubric: CL-7, CL-8, CL-10, CL-11 and CL-13.
  - CL-9 and CL-12 are reused for chapters 9 and 12.
  - The pacing guides reference all of them.
- **SME tag:** "Pending SME review" appears as an instructor-only note on every expanded lesson and is stripped for students (checked: students see 0 tags, instructors see the tag). It is also on the lesson plans, lab manual, answer-key bank and glossary (†).
- **Contrast fix:** inline `code` inside core content is darkened in the light theme. axe found Bootstrap's pink at 4.2:1 on the worked-example panels.
- **Tests:** `tests/test_itsup_expansion.py` enforces depth, structure, figure accessibility, objective verbs, item quality and balance, and the SME tags. `test_curriculum_integrity.py` counts the expansion items toward objective coverage.

**Tests (end of pass)**
- pytest: 214 passed, including the content-integrity and expansion tests.
- node: 31 passed.
- Phone e2e: 43/43 in light and 43/43 in dark.
- axe-core, full sweep of 123 page/width checks per theme:
  - Dark: 0 violation nodes.
  - Light: 29 colour-contrast nodes on lessons 13.1 and 13.4, all inline code in worked examples.
  - After the fix, all lesson pages were re-run (15 checks per theme): 0 violations.
  - The sweep now includes lessons 7.1, 10.1 and 13.4, the instructor view of 13.1, and the lab manual.
  - Reports are in `/workspace/artifacts/pass9-reports/`.
- Screenshots are in `/workspace/ciwt/screenshots/pass9/`.
- The course package was rebuilt: 44 DOCX/PDF files in `/workspace/artifacts/course-package/` and `course-package.zip`.

**Still open:** SME review of everything tagged. Chapters 3–6 are the next thinnest. A separate worker is overhauling the interactive labs on the `labs` branch. `course_package.py` (CLASSROOM_LABS, pacing rows) changed here too, so expect a merge point there.

## Pass 10 (Oct 17 2026): accuracy study, calibration quality, session hardening, privacy tools, ITSUP ch 3–6

### Helix: accuracy study (consented, ground truth only)
- **Separate consent** at `/helix/study` (`HelixStudyConsent`, version `2026-10-17.s1`), independent of lesson consent. Students can leave at any time; leaving offers to delete their study records.
- **What is collected:** only gaze-derived ground truth from calibration/validation: error in px and degrees, precision, estimated distance, calibration time, per-validation-point error (`points_json`), and the device class, browser family + major version, camera resolution, viewport and DPR. No images, no landmarks, no lesson data. `POST /api/helix/study/record` needs study consent and is rate-limited.
- **A/B arms:** `/api/helix/study/arm` assigns the calibration method (9 dots / follow-the-dot) and hiRes on/off, balanced per device class; the second round in a visit changes exactly one factor, so each visit gives a within-person pair (`pair_id`).
- **Admin view** `/admin/helix/accuracy` (+ `.csv`): aggregates per device class, browser and resolution, plus paired arm comparisons. It shows nothing for groups under 5 users, and only reports an arm difference with ≥10 pairs, p<0.05 (sign test) and a gain of ≥0.5°. It **never switches defaults by itself**; an admin can set per-device-class defaults (`HelixCalibDefault`) by hand, and the page shows the evidence next to the control.
- **No real-user records exist yet.** The e2e study run (`tools/helix_study_e2e.py`) uses a fake camera with no ground truth and deletes its own records.

### Helix: re-check and the instructor calibration view
- Students get **Re-check accuracy** in the dock: a validate-only pass showing the accuracy now against the last calibration, with "Keep going" / "Recalibrate". Stored per session as `rechecks`, `recheck_error_px/deg`.
- Sessions now also record `calib_ms`, `calib_mode` (full/quick/recheck), `camera_losses`, `sleeps`, `tab_yields`, `camera_res`, `hires`, `browser` (disclosed in the policy table; policy version bumped to `2026-10-17.3`).
- Instructors: **Calibration quality** (`/instructor/section/<id>/attention/calibration`) shows per student their camera sessions, accuracy band and median validation error, median calibration time, recalibrations and re-checks, the last re-check, interruptions (camera losses, sleeps, other-tab) and device/camera. The page says it is for judging how far to trust the attention data and who needs setup help, and that it says nothing about how well anyone learns.

### Helix: session hardening (simulated in `tools/helix_hardening_e2e.py`, all six steps pass)
- **Multiple tabs:** tabs coordinate over a `BroadcastChannel`; when another tab starts tracking, this one releases the camera (time recorded as "other tab", `tab_yields`) and can take it back.
- **Sleep/resume:** a timer gap is recorded as "Device asleep / page suspended" (`sleeps`) instead of face-lost time; a gap over 15 minutes ends the session automatically with a "Resume with a new session" button.
- **Camera unplugged, track ended, permission revoked:** the session switches to a "Camera off" state (`camera_losses`), says plainly that nothing is being measured, and reconnects when the camera comes back; a loss before the session goes live ends it cleanly.
- These are browser simulations (fake device, `track.stop()`, visibility and timer events), not tests on real hardware.

### A/B: hiRes and follow-the-dot
See `tools/helix_eval/RESULTS.md` (pass 10). On recorded proxy video, follow-the-dot + 3 points improved with 1080p input on both subjects (16/20 sequences, p=0.012) but that is only 2 people and costs ~48 vs 33 ms per frame. **Defaults are unchanged** (9 dots; 720p on desktop/tablet; 480×640 on phones). The study above is how they should change: ≥10 real pairs, p<0.05, ≥0.5°.

### Privacy and operations (steering items)
- **Debugger off by default.** `python app.py` / `./start_lms.sh` run with debug off; `FLASK_DEBUG=1` turns it on and binds to 127.0.0.1 (overridable only with `CIWT_ALLOW_DEBUG_ON_NETWORK=1`). `run_settings()` in `app.py` holds the rule; README documents it.
- **Neural Listen voice switch.** `CIWT_NEURAL_TTS=0` disables `/api/narrate` (403 `{fallback, disabled}`); lessons then hide the neural voice picker and use the browser voice, preferring voices marked on-device. Default is still **on**. The new `/privacy` page (linked from the footer and the Helix policy) says that the neural voice sends lesson text to Microsoft's online speech service through edge-tts.
- **Admin → Privacy** (`/admin/privacy`, link per student in People): preview, export (JSON, secrets such as password hashes and API tokens removed) and delete a student's full record. The table list comes from the database schema (`privacy_tools.plan`), so new tables are covered automatically: rows owned by the student are deleted, shared rows that only mention them (audit log, "updated by") are kept with the reference set to NULL and the audit IP blanked. Deletion requires typing the student's email, is refused for staff accounts, and every export/delete/cleanup is written to the audit log (by user id, not email).
- **Helix retention:** `CIWT_HELIX_RETENTION_DAYS` (default 365, 0 = keep). `flask --app app helix-cleanup [--dry-run]` for cron, or the button on the admin page, deletes sessions (with AOI rows), attention events and accuracy records older than the cutoff. Consent records are kept.
- Tests: `tests/test_privacy.py` (run settings, TTS switch, privacy page, admin-only access, export, delete with a throwaway student, retention, CLI).

### ITSUP chapters 3–6 (pending SME review)
Chapters 3–6 now have the same core-content layer as 7–13 (`curriculum_v2/itsup_core/ch03.py`–`ch06.py`): measurable lesson
objectives, explanations, worked examples and scenarios, eight described SVG figures, CFUs, 55 glossary terms, lesson-plan
updates and 46 items (IT-3.1–6.3, ≥2 per objective). Facts were checked against the named sources; details, the SME notes and the
**lab gaps for the labs worker** are in CURRICULUM_AUDIT.md (“Pass 10”). No lab formats were changed. Documents and docstrings
that said “chapters 7–13” now say 3–13.

## Pass 11 (Oct 17–18 2026): adaptive mastery engine

Package `mastery/` (pure model/policy/memory/diagnosis modules + Flask routes), templates in `templates/mastery/`,
styles in `static/css/mastery.css`, misconception tags in `curriculum_v2/misconceptions.py`. Every estimate and decision is a
learning aid: **nothing here reads or writes a grade** (tested), and everything is explained to the student ("Why am I seeing this?").

### The model (transparent BKT with confidence) — `mastery/model.py`
- One estimate per objective (50 in ITSUP). Bayesian Knowledge Tracing: prior 0.30, learn 0.12, slip 0.10, guess 0.25 (labs 0.10).
- Each answer is a tempered Bayes update `p ← p + w(post − p)` then a learning step `p ← p + (1−p)·learn·w`. Weights: graded test 1.0,
  mastery check (test-out) 1.0, chapter check 0.8, lab 0.7, review check / daily review / in-lesson quick check 0.6.
- **Time on task:** reading a mapped lesson for ≥ half its estimated minutes gives +0.05 learning credit. Too little time never lowers p.
- **Confidence** = effective evidence n_eff (sum of weights): low < 2, medium < 6, high ≥ 6. Mastered ≥ 85 % (medium+); needs review < 60 % with n_eff ≥ 1.5.
- **Helix is never an input** to an estimate. With current consent and Helix on for the class it can only produce an *optional* review offer;
  no consent or no data → the rule simply does not fire (tested: "Helix never penalizes", consent fallback).
- Seeded test attempts whose answer texts no longer match current options are **skipped as stale** (shown as a count on the instructor student page), never guessed at.

### Policy and actions — `mastery/policy.py`, `mastery/engine.py`
- Waive > force review > engine; objective overrides beat chapter (`CH-n`) overrides. Force review works even with adaptivity off; Lock makes reviews required and blocks test-out; Unlock opens test-out.
- Engine: needs review → short targeted review (3 items, reused lesson sections + glossary, no new facts) → alternate explanation → after 2 completed reviews "stuck" for the instructor. A skipped review is not re-inserted until new evidence.
- Required reviews are inserted **before the next lesson** (lesson route redirects 303; the review's own lesson stays open).
- Test-out: offered per chapter to strong students (≥ 3 objectives, 80 % strong) or by Unlock; 2 items per objective (max 12) from the item bank; pass = 80 % and ≥ 1 right per objective; max 3 attempts.
- Student home "Your path" card (`mastery/_path.html`) and the hero Continue follow the engine; every step has "Why am I seeing this?" with the evidence.
- Every decision is logged in `mastery_decision` with reasons and an evidence snapshot.

### Instructor page — `/instructor/section/<id>/mastery`
Student × objective heatmap (chapter filter, AA chips, 44 px cells, screen-reader names), who is stuck and why, inserted reviews, decision log,
overrides dialog (lock / unlock / force review / waive / clear, note required, audited), adaptivity + test-out toggles, CSV export, per-student evidence page.

### The six additions
1. **Misconception detection** — 56 misconceptions, 136 (item, distractor) tags on IT-1.1–1.4, 5.1, 5.3, 8.4, 10.1, 10.3, NO-1.2, 2.1, 2.3, 3.1, 5.1.
   Every tag was checked against the bank (a real distractor, never the key); fixes are worded from the items' own explanations. A tagged pick turns
   the review into "Fix a mix-up" (the mix-up, then what the lessons say instead, from the two best-matching lesson sections). Counts per student
   (`misconception_summary`: hits, last hit, resolved by a later right answer) and per class (Who needs me). Untagged objectives fall back to the normal review.
2. **Spaced retrieval** — `mastery/memory.py`, SM-2 style per objective: ease 2.5 (+0.05 per recalled day, max 2.8; −0.2 per lapse, min 1.3); intervals 1 → 3 → prev × ease, lapse → 1;
   a day counts as recalled at ≥ 60 % right. Predicted recall R(t) = 0.9^(t/interval): due when it reaches 90 %. **Daily review** card on the student home: 5–10 due
   questions, "about N min" at 30 s per question, ungraded, one per day (`/student/section/<id>/daily`).
3. **In-the-moment struggle detection** — one quick check per lesson section (`_quickcheck.html`, `mastery-lesson.js`). A miss plus (Helix re-read of that section *with consent*) or
   (≥ 45 s on the section without Helix) or a tagged distractor → an inline alternate explanation from the lessons. It is an offer: dismissible, logged, never required, never graded; the key is never sent to the browser.
4. **Lab process diagnosis** — `mastery/lab_diagnosis.py`: `diagnose(events, lab=None)` takes the labs branch `LabEvent` list (dicts or objects: seq, kind, action, outcome, newly, detail)
   and returns patterns `trial_and_error`, `repeats_without_change`, `never_verifies`, `skipped_step`, `hint_reliance`, `efficient`, each with evidence and a coaching tip.
   Tested with hand-written fixtures (`tests/fixtures/lab_events.json`, marked as not real data). **Not wired to live labs** (labs branch untouched). The merge needs:
   (a) pass `lab_events=lambda uid, sid: {lab_id: events_for(uid, lab_id, latest_attempt)}` in the mastery deps in `app.py`, filtering `LabProgress.section_id == sid`;
   (b) pass the lab definition (`interactive_labs.get_lab(lab_id)` objectives in order) as `lab=` so `skipped_step` can fire; (c) optionally list diagnoses on the instructor student page.
   Until then the "lab struggle" reason in Who needs me stays off.
5. **Instructor "Who needs me"** — `/instructor/section/<id>/mastery/today`: daily ranked list with plain reasons (stuck, repeated mix-up ≥ 2, review waiting > 3 days or ≥ 2 skips in 14 days,
   ≥ 20-point drop in 7 days, lab struggle when wired, 7 days inactive); ranked by number of different reasons, then most serious, then most recent. No risk score.
   One-click actions: message (preselected recipient), assign review (force review override), schedule check-in (date, logged + audited). Inactivity-only students are folded away.
6. **Student-owned learning plan** — `/student/section/<id>/plan`: mastery map, review style choice (short review / alternate explanation / practice questions), daily size 5–10, target exam date
   (after today, ≤ 2 years) with a backward plan: objectives to master per week and the review load per week. Status ahead / on track / behind is about the plan only; the page says it is **not a prediction** of an exam result.

Out of scope as agreed: confidence-weighted answers and pass forecasts.

### Tests and tools
- pytest: `tests/test_mastery.py` (model math, overrides, consent fallback, Helix never penalizes, routes, gradebook unchanged) and `tests/test_mastery_features.py` (the six additions). Suite: 302 passed.
- `tools/mastery_e2e.py` (Playwright, throwaway server + DB copy): review inserted → why panel → lesson banner → mix-up correction → inline offer + dismiss → daily review → plan →
  heatmap + override dialog (force review → required and redirected before the lesson → waive) → Who needs me → chapter unlock → test-out passed. 38/38 at 1280 and 390 (light), 390 dark.
- axe WCAG 2.1 AA sweep (`tools/a11y_sweep.py --themes light,dark`, mastery pages added): 360 page/width checks, 0 violations, no overflow. Mastery pages also in `tools/site_audit.py` and `tools/shots.py`.
- Other runs (throwaway server on :5078, DB copy): `site_audit.py --themes light,dark` no overflow anywhere (instructor mastery page: 1 small target left at 390 px, the adaptivity switch); `assess_phone_e2e.py` 43/43; `helix_lesson_e2e.py` and `helix_hardening_e2e.py` pass with the face y4m; node 31/31. `helix_e2e.py` times out waiting for calibration dots because it predates the "Get into position" step (added in commit 2bda572, before pass 11; Helix JS is unchanged in this pass), so that script needs updating, not the runtime.
- Fixes found by the sweep: heatmap cells use hidden text for their name (label-in-name), darker link in the why panel (contrast), long Next buttons wrap, scrollable lesson tables get focus after web fonts load (`base.html`).

### Known limits
- Model parameters are literature-typical defaults, **not fitted** to this course: no real student data exists (the demo accounts are seed data and every page says so).
- Misconception tags cover 14 of the most-used objectives; the rest get the plain review. Tags and fixes need SME review like the pass 8–10 content.
- Struggle detection without Helix uses time on the section, which cannot tell reading from an idle open tab (only counted while the tab is visible).
- The memory model is SM-2 style, not a fitted FSRS; due dates are per objective, not per item.
- Lab diagnosis is heuristic (e.g. `never_verifies` keys on verify-like commands) and only tested on fixtures.
- Next step: instructor co-pilot briefing (a daily summary built from Who needs me + the decision log) and process-graded labs once the labs branch is merged.
## Labs branch (Oct 18 2026): every lab works on desktop/phone/tablet; real Linux VMs are standard

Details: `LABS_AUDIT.md` (audit, fixes, per-lab results), `REAL_ENVIRONMENTS.md` (real vs simulated per lab, networking,
Windows), `docs/VM_IMAGE.md` (image, measurements, institution build recipe). Merged `refinement` at bc19ca8.

- **Counts:** 46 → **69 labs** (23 new; 5 of them real Linux VM labs) plus 9 classroom labs (CL-4, CL-6…CL-13) with instructor
  sign-off. Kinds: windows 25, switch 11, activity 9, win11gui 8, router 8, vm 5, ticket 2, linux 1.
- **State in the DB:** `lab_progress` (one row per student and lab) replaces the session cookie, so labs resume after reload
  or re-login. Completion is graded on the server, and a client can no longer fake it. **Undo/reset/hints**,
  "did you mean", aliases and tab completion work in every terminal.
- **Process log:** `lab_event` keeps an ordered log per attempt of each command, GUI action, check, hint, undo, reset,
  VM probe and completion. You can view it per student (`/instructor/section/<id>/labs/student/<uid>`) or export it
  (`…/labs/events.csv`).
- **Gradebook:** new `labs` category, default weight 0, so existing grades don't change. The syllabus lists the category.
- **Mobile:**
  - The terminal has a keys bar, focus mode and no zoom on input.
  - Windows 11 GUI labs reflow into a narrow mode. Long-press works as right-click.
  - Activities support drag and drop, with tap-to-place as a touch alternative.
- **Real environments:** linux-vm-perms, -shell, -services, -netclient and -routing run real Linux in the browser (v86,
  self-hosted, pinned with SHA256, fetched by `tools/fetch_v86.sh`):
  - They boot in about 3 s, with save/resume through IndexedDB and an instant reset from a snapshot.
  - Grading reads the real VM state through a probe script and combines it with command history and evidence from the
    virtual network (`static/js/lab-vmnet.js`: a switch, ARP/ping, a DHCP server and a DNS server).
  - linux-vm-routing runs two VMs that route between two segments.
  - Weak devices get a link to the simulated twin.
  - Windows stays a high-fidelity simulation, because in-browser Windows isn't viable. A hosted-VM option is noted.
- **Tests:**
  - pytest: `tests/` 440 passed, including `tests/test_vm_real.py`, which boots each VM lab headlessly in Node and grades
    both the solution run and an empty run.
  - Node: 35/35 tests (`tests/js`).
  - e2e: `tools/labs_e2e.py` passed 246/246 (78 labs × desktop/phone/tablet + 12 instructor checks).
  - `tools/vm_device_check.py` covers throttled phones: boot, save/resume, reset and an axe check.
  - Screenshots are in `/workspace/ciwt/screenshots/labs/`.
  - After the merge of `refinement` at ee0a353 (pass 11):
    - pytest: 477 passed.
    - e2e sample (13 labs of every kind × desktop/phone, plus instructor checks): 35/35.
    - axe on every lab page at 390/820/1280 px: 0 violations in light and dark themes. Fixed two contrast bugs: the
      router tag, and the Windows 11 desk in dark theme.

### Labs branch, round 2/3 (Oct 18 2026): 15 real Linux labs, Windows fidelity, lab scenarios (all *Pending SME review*)

- **Counts.** 79 labs (46 original + 33 new) and 2 lab scenarios with 4 PBQ stage labs, plus 9 classroom labs.
- **Real labs.** 15 real Linux VM labs (+10 this round: logs, cron, users/sudo, packages, iptables, disk/fstab, SSH
  keys, scripting, DNS chain, DHCP/route fault) and 2 real-VM scenario stages. Windows and IOS remain simulations.
- **VM image.** An own build, `ciwt-linux.bin`: 10,781,184 B, 13.3 MB first download. See `docs/VM_IMAGE.md`;
  licences and the GPL source offer are in `static/vendor/v86/LICENSES.md`.
- **Windows sims.** `win_fidelity.py` adds realistic output, elevation errors and wrong-turn branching. Grading is
  unchanged.
- **Scenarios.** `labs_scenario.py` adds SCN-DNS and SCN-LAN2 with hidden checks; hints and the event log are kept.
- **SME tag.** Every new lab, stage and scenario carries `review: "Pending SME review"`, shown to instructors only.
- **Final run (3e6d0ab):**
  - pytest: 539 passed
  - Node: 36/36
  - e2e: 288/288 (92 lab pages × desktop/phone/tablet + 12 instructor checks)
  - axe sweep of the lab pages: 0 violations in light and dark (one light-theme contrast fix on the scenario hub)

## Pass 12 (Oct 18 2026): briefing, LTI 1.3, labs + content merges

Local work only: nothing was pushed. Every server and e2e run used a copy of the DB (`/tmp/p12/work.db`, `/tmp/p12/fresh.db`).
At the end, `ciwt_lms.db` is at its baseline sha `47fabc92…`.

During the pass, two ad-hoc inspection scripts imported `app` without `DATABASE_URL` set. That ran the start-up sync
against the real `ciwt_lms.db` and changed it. I caught this with a sha check and restored the file byte for byte
from `dbsnap/ciwt_lms.pass6-before.db`, which has the baseline sha. The changed copy is kept at
`/tmp/p12/ciwt_lms.mutated-0130.db` for reference. Ad-hoc scripts now always export `DATABASE_URL` to a copy.

### Merges
- **`labs` (3350882).**
  - Merged cleanly.
  - The 10 VM tests need `tools/fetch_v86.sh` (pinned and sha-checked; the binaries are gitignored).
- **`content` round 1 (be25252).**
  - Merged following MERGE_NOTES_CONTENT.md.
  - `a11y_sweep.py` and `site_audit.py` keep both page lists. The icon subset was rebuilt, and
    `cert_coverage.py` / `cert_coverage_md.py` were re-run.
- **`content` round 2 (e01b923).**
  - Conflicts were limited to CERT_COVERAGE.md, alignment.json (regenerated) and a11y_sweep (union; the coverage
    filter is now `status=covered`).
  - Coverage: A1/A2/N at 100% weighted.
  - `curriculum_v2/misconceptions.py` now imports the cert tags (the three lines from the merge notes, placed before
    `_NORM` is built), adding 83 `MC-C-*` misconceptions and 277 tags.

### Mastery engine changes
- **Typed items** (multi-select, ordering, matching) are judged all-or-nothing by `engine.judge()`.
  - Before this they were miscounted as "stale".
  - An answer that uses options the item no longer has is still treated as stale.
- **Review, daily, test-out and inline pools stay single-answer**, because those UIs are radio-only.
- **Practice exams count as evidence at weight 0.8.**
  - Only submitted attempts count, and blank answers are skipped.
  - Attempts are account-level, so they count in every class of the course.
  - They never appear in the gradebook (tested).
  - Wrong single answers now carry `MC-C-*` tags too.
- **Cert items join the pools (round 2).**
  - `engine.pool()` now serves, in order: the class's chapter-check items, then aligned single-answer cert items
    (`cert_items_for(obj)`: 238 items over 48 objectives; Pending SME review), then the X-IT bank and supplement if
    the class turned that on.
  - The pick order is least-used first, then that source order (`SRC_RANK`).
  - This feeds reviews, struggle and misconception offers, daily practice, test-outs and in-lesson checks.
  - A tagged wrong cert answer surfaces as a misconception (tested).
  - The instructor mastery page says so.

### Lab process diagnosis wired in
- `mastery/lab_source.py` reads `lab_event` for the latest attempt per lab (1 + resets), limited to `LabProgress`
  rows of this class. `lab=` comes from `interactive_labs.get_lab`.
- **How event kinds are mapped:**
  - `vm` lines are actions, except `vm boot`, and are never "rejected".
  - A `vm probe` check counts as rejected only on `error`; "not finished" is not rejected, but repeating it unchanged
    is flagged.
  - Guided `check` answers that come back wrong are rejected.
  - Hints count only on `ok`; `repeat` is a re-view.
  - Linux read-only commands count as verification.
- **Where diagnoses show up:**
  - "Who needs me" has a lab-struggle reason.
  - The instructor student page has a "How X works the labs" section, with an event-log link and coaching tips.
  - The briefing has a lab-struggles card and to-do items.
- Patterns never change a lab score (tested).

### Instructor co-pilot briefing (`mastery/briefing.py`)
- **Pages and exports:**
  - `/instructor/section/<id>/briefing`, plus `.txt` (email-ready text, download only) and `.csv`.
  - A card on the instructor home with the top item per class, cached for 5 minutes.
  - Links from the class page and the sidebar.
- **It is deterministic. No AI model writes any of it.**
  - Candidates are scored with visible formulas:
    - mix-up: 3 × students with it active (at least 2)
    - student: 2 × reasons, +2 if stuck
    - objective: 2 × students below mastered
    - lab: 2 × students
    - section: students who skimmed or skipped it
    - assessment: low attempts
  - The top 3 are chosen one per kind first, then by score, with deterministic ties.
- **One-click actions:**
  - jump to the re-teach
  - assign review to those students (bulk `force_review`, logged and audited)
  - message
  - check in (returns to the briefing)
  - open the heatmap, the lesson or the result
- **Content of the page:**
  - **Re-teach.** Each re-teach takes 5 minutes (1 + 2 + 2). It is built from the course's own `fix` text, the lesson
    blocks (instructor notes stripped), and a tagged question from the check, cert or test pools showing the tempting
    answer.
  - **Skimmed and skipped sections.** These come from Helix data, but only for consented students and non-demo
    sessions of at least 60 s. A section is skipped at 0 ms and skimmed under 3 s. It is listed only when at least 2
    measured students and at least half of them skimmed or skipped it.
  - **Other sections:**
    - objectives most of the class has not mastered
    - who to check in with
    - results from the last 7 days
    - what is coming up (releases and check-ins)
    - engine log counts
    - "How this briefing is made"
- **Accessibility and output:**
  - The demo ribbon carries through.
  - Mobile-first, with print CSS.
  - axe finds 0 violations at 390/820/1280 px in light and dark.
- Nothing is sent anywhere (tested).

### LTI 1.3 + LTI Advantage, tool side (`lti/`; see docs/LTI_SETUP.md)
- **Built on PyJWT and cryptography** (added to requirements.txt).
- **Endpoints:**
  - OIDC login initiation: `/lti/login`, with `?reg=` for disambiguation.
  - Launch: `/lti/launch`. It checks:
    - a single-use 10-minute state, bound to the browser by a cookie, and a single-use nonce
    - the id_token against the platform JWKS by kid, with one refresh on rotation
    - RS256/384/512 only
    - iss, aud, azp, exp, iat (max age), version, message type, deployment, resource link and deep-link settings
  - Tool JWKS: `/lti/jwks`. The key comes from `LTI_PRIVATE_KEY`, `LTI_PRIVATE_KEY_FILE` or `instance/lti/` (0600,
    gitignored), with rotation through `instance/lti/previous/`.
  - `/lti/config.json`, and a Canvas developer-key JSON.
- **Accounts:**
  - People are mapped by (platform, sub).
  - Linking by email is opt-in per platform and never touches admin accounts.
  - New accounts get a random password.
  - LMS roles map to instructor or student, never admin. Existing roles are never changed.
  - Learners are enrolled in the mapped class. Instructors map an LMS course to one of their classes.
- **Deep Linking 2.0:**
  - The instructor picks lessons, chapter checks, tests, labs or the class home.
  - Graded items get a `lineItem`.
  - The response JWT is signed and auto-posted. The picker is single-use, valid for 1 hour, and tied to its owner.
- **AGS:**
  - Scores are sent from the gradebook, with late penalties, overrides and excused cells applied; missing and excused
    cells are skipped. Labs send the best lab score; the class home sends the course grade.
  - Uses client-credentials JWT assertions.
  - Finds or creates the line item.
  - Sends happen only on the instructor's button press.
- **NRPS:**
  - Follows `Link: rel=next` paging.
  - Enrolls learners, links staff, counts inactive members, and removes nobody.
- **Admin UI:** `/admin/lti`, with Canvas, Blackboard, Moodle and other presets and HTTPS validation. The class page
  is `/instructor/section/<id>/lti`, with a sync log.
- **Mock platform:** `tools/lti_mock_platform.py`, in memory, with fictional demo people on `mock-lms.invalid`.
- **Tests:**
  - `tests/test_lti.py` has 15 tests: each refused claim, roles, JWKS and key handling, launch and enrollment, state
    replay, missing cookie, email-link safety, the deep-link round trip, learner DL refusal, AGS score POST, NRPS
    paging, access and admin validation.
  - `tools/lti_e2e.py` drives a real Chromium run: 9/9.
- **Honest status:**
  - Not 1EdTech-certified.
  - Not tested against a live Canvas, Blackboard or Moodle.
  - Platform Storage, Dynamic Registration and automatic score sync are not done.

### Other
- `tools/helix_e2e.py` walks the "Get into position" step. It now checks properly and exits non-zero on failure:
  6/6.
- The CSRF form test allows `data-external-post` forms. That is the deep-link auto-post to the LMS, which must not
  carry our token.

### Results at the end of pass 12
- `pytest tests`: 547 passed, run with the VM assets fetched.
- node: 40/40.
- axe:
  - all 202 page/width checks per theme, at 390 and 1280 px, in light and dark.
  - Ended with 0 violations after one fix: the LTI sync log `<pre>` scrolled at 390 px.
  - The briefing and LTI pages also pass at 820 px.
- site_audit: every page returned 200, except the intended 403/404 pages. There was no overflow.
- e2e suites:

  | Suite | Result |
  |---|---|
  | mastery_e2e | 38/38 |
  | helix_e2e | 6/6 |
  | assess_phone_e2e | 43/43 |
  | practice_phone_e2e | 29/29 |
  | lti_e2e | 9/9 |

## Pass 13 (Oct 18 2026): DB guard, cert-item switch, curriculum readiness, semester simulation, misconceptions, first-run

**DB safety (1ca65e1).** Importing `app` without `DATABASE_URL` now fails unless `CIWT_ALLOW_REAL_DB=1` is set,
so tests, tools and stray scripts can no longer write to `ciwt_lms.db` by accident. `start_lms.sh`, `Procfile`
and `render.yaml` set the flag, so production start is unchanged. The change is covered by
`tests/test_db_guard.py` and documented in the README.

**Cert-item switch (177183f).** Mastery settings has a per-class switch, "Include certification practice items
(pending SME review)". It is on by default. The `mastery_setting.cert_items` column is added by a migration.
When the switch is off, reviews, daily review, test-outs and in-lesson checks use only the class's chapter-check
items. Tests are in `tests/test_mastery_cert_round2.py`.

**Curriculum readiness (f0379f6, 73ff97b, 51e9922).** The audit is `tools/curriculum_readiness.py`, and the
course package now has a `MANIFEST.json` with per-document hashes. The audit passes 25/25 on ITSUP and NETOPS;
see `CURRICULUM_READINESS.md` and `docs/readiness/readiness-pass13.json`. Real fixes:

- first boot now runs the content syncs;
- lesson-plan minutes are now the sum of the LMS lessons;
- duplicate stem X-IT-9.2.2 removed;
- from the 40-item spot-check against primary sources: N2.8 stem fixed and X-IT-9.4.1 rationale fixed, with 0
  wrong keys.

The SME review list is in CURRICULUM_READINESS.md:

- 62 terse rationales;
- 415 cert items still pending review;
- NETOPS ch9 lessons are short;
- objectives without check or cert items;
- credit-hour assumptions.

**Adaptive semester simulation (ce3cdab).** This is a synthetic check, not evidence of learning gains.
`tools/semester_sim.py` runs 20 synthetic accounts (`@synthetic.invalid`, in a clearly labelled class) through
ITSUP chapters 1–4 for 28 simulated days using the real routes. The latest run (seed 13) passed 12/12 checks.
`tests/test_semester_sim.py` is the 22-day smoke version. It found one real bug: reading-only objectives blocked
mastery-check offers (`policy.strong_so_far` now counts only answered objectives). See
`docs/SEMESTER_SIMULATION.md`.

**Misconceptions (3317db1).** Every chapter-check objective now has misconception tags (63/63): 109 new
misconceptions and 314 new tags, for 248 misconceptions and 727 tags in total.

**First-run experience (7f2b83f).** Instructors see a "Set up your class" checklist on the class page with five
items:

- adaptive path;
- Helix attention policy;
- certification items;
- release the first chapter (marked done automatically once something is released);
- connect your LMS (optional).

Each item shows its current value, a settings link, and "Looks right" or "Skip for now" buttons. The checklist
can be hidden and shown again per class. Students see a one-time "How your path works" card covering the next
step, short reviews, daily review, mastery checks and "none of this changes your grade". "Got it" dismisses it
for good. Both are stored in `onboarding_flag`; neither changes a setting or a grade. The checklist and the intro
card are styled phone-first. axe found 0 violations on them in light and dark at 390 and 1280. Tests are in
`tests/test_onboarding.py`.

**Results.**

- pytest: 566 passed.
- node: 40 passed.
- a11y sweep: 606 page/width/theme checks, 0 violation nodes.
- site_audit, light and dark: no unexpected errors. The intentional 403/404 pages and `msg-thread` without
  `--prep` return 403/404 as expected.
- mastery_e2e: 38/38.
- helix_e2e: 6/6.
- practice_phone_e2e: 29/29.
- lti_e2e: 9/9.
- assess_phone_e2e: 43/43 on a fresh DB copy. It needs its own copy, because it fails if another suite has
  already taken test 1/2.
- The readiness audit and the simulation were re-run after the package rebuild: 25/25 and 12/12.
- `ciwt_lms.db` sha256 is unchanged (47fabc92…).

**Screenshots.** In `/workspace/ciwt/screenshots/pass13/`: `setup-checklist-*`, `student-intro-*` and
`cert-switch-*` at 390 and 1280 in light and dark, `semester-sim-{390,1280}.png`, and `onboarding/` (full pages
plus the axe report).

**Known limits.**

- A test-out skips the chapter check, so completion % drops if quiz weight is above 0.
- The briefing to-do breaks ties alphabetically.
- The LTI deep-link test fails when run alone with `-k`; the whole file passes.
- The onboarding checklist marks review state only. It never changes settings; changes happen on the linked pages.
- SME review is still required for the cert items and the terse rationales.

**Next steps.**

- SME review of the CURRICULUM_READINESS list.
- Fill in rationales.
- Add check items for the IT-x.4 objectives in ch7–13.
- Pilot with real students before claiming any learning effect.
