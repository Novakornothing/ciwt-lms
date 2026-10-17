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
