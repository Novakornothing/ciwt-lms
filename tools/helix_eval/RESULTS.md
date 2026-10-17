# Helix gaze pipeline: what was measured, and how

Generated 2026-10-17 on this build box (8 vCPU, no GPU, headless Chromium). Every number below was
produced by a script in this folder or `tools/`, and you can re-run it. **No real person looked at
known targets for any of these numbers.** Real-device accuracy is still **unmeasured** (see the end).

## 1. Synthetic accuracy harness (`node tools/helix_eval/eval.js --users 20 --json results.json`)

The simulator (`synth.js`) is a deterministic geometric eye/head model. Each user gets their own
kappa angle, IPD and eyeball size. The lids follow vertical gaze. Fixations jitter, and landmarks
get pixel noise. It is projected through a 640×480 pinhole camera with a 60° FOV, onto a 1440×900
screen at 0.0213 cm/px, from 55 cm. It produces MediaPipe-shaped landmarks plus a head-pose
matrix. Those go through the **same** `helix-model.js` code the browser runs:
- 9-point calibration, 22 frames per point
- validation on a 4×4 grid of **unseen** targets

| condition | point error, median px (°) | p90 px | smoothed per-frame error px (°) |
|---|---|---|---|
| baseline (0.8 px landmark noise, head still) | 75 (1.63°) | 110 | 91 (1.98°) |
| low noise 0.4 px | 32 (0.69°) | 43 | 35 (0.76°) |
| high noise 1.6 px | 185 (4.03°) | 218 | 196 (4.35°) |
| phone-like: 30 cm, 390×844 | 27 (0.88°) | 34 | 28 (0.97°) |
| head moved 4 cm + 5° yaw after calibration | 188 (4.09°) | 310 | 199 (4.05°) |
| … same, after 20 implicit clicks | 89 (1.88°) | 123 | 111 (2.36°) |
| ablation: single ridge, head moved | 442 (9.2°) | 821 | 466 (9.6°) |
| head leaned 8 cm closer | 134 (3.46°) | 227 | 133 (3.29°) |

What this shows:
- The hybrid geometric + residual model keeps working when the head moves; a plain ridge model
  does not (4.1° vs 9.2°).
- Implicit click samples recover most of the loss (1.9°).
- Landmark noise is the dominant factor.

What it does **not** show: real-world accuracy. Real eyes, glasses, lighting, webcam optics and
MediaPipe's own landmark bias are not in the model.

## 2. Real face video through real MediaPipe (`tools/helix_mp_e2e.py`, `tools/helix_lesson_e2e.py`)

**Camera:** Chromium's fake capture device playing a CC0 interview clip
(Wikimedia Commons "Interview with Zara Kay about Faithless Hijabi.webm", 2:00–2:24, cropped to
640×480 at 15 fps).

**Delegate:** CPU. SwiftShader "GPU" was 330–1100 ms/frame on this box. Real GPUs are expected to
be fast, but that is **untested** here.

| measured | desktop 1280×800 | phone emulation 390×844 (touch, portrait) |
|---|---|---|
| engine load (bundle + 3.7 MB model + WASM) | 0.4 s (localhost) | 0.4 s |
| face found | 100% of frames | 100% |
| inference | 20–23 ms/frame | 23–25 ms/frame |
| achieved fps (cap) | 13.5–14.5 (18–19 adaptive target; source video is 15 fps) | 10.5–12 (15 cap on mobile) |
| positioning guidance | satisfied (distance ~39 cm, centred, facing, level, eyes, light) | satisfied (~27–30 cm) |
| calibration | 9/9 dots, 87–108 training frames | 9/9 dots (tap), 87–102 frames |
| live estimates | 138–195 in 9 s, moving: x SD 347–417 px, y SD 194–304 px | 188, x SD 64, y SD 247 |
| validation "error" | 454–827 px | 254–329 px |

The validation error in this row is **meaningless as accuracy**. The person in the video is talking
to an interviewer, not looking at our dots. The row only proves that every stage runs and that the
estimates respond to her eye and head movement.

On the real lesson page (`helix_lesson_e2e.py`), the server stored:
- `engine=mediapipe`, `delegate=CPU`, `validation_error_deg`, `distance_cm`, `aoi_resolution=heading`
- `orientation`: landscape on desktop, portrait on mobile
- AOI buckets and a `drift_json` marker

Implicit samples were 0 because the gate correctly rejected clicks that were 450+ px from the
estimate. The video person was not looking at what the script clicked.

### Final re-run (2026-10-17 ~15:20 UTC, same clip, CPU delegate)

| run | engine / delegate | inference | fps (cap) | face | live estimates | validation "error" (not accuracy) |
|---|---|---|---|---|---|---|
| Try page, desktop 1280×800 | mediapipe / CPU | 24.8 ms | 10 (15) | 100% | 124 in ~9 s, x SD 287 px, y SD 234 px | 419 px ≈ 16.7° at ~37 cm |
| Try page, phone emu 390×844 | mediapipe / CPU | 27.3 ms | 11 (15) | 100% | 191, x SD 73 px, y SD 203 px | 321 px ≈ 17.0° at ~28 cm |
| Lesson page, desktop | mediapipe / CPU | 25.1 ms | 13 (17) | 100% | stored session 35: 140 samples, 6 AOI buckets | 527 px ≈ 20.5° |
| Lesson page, phone emu | mediapipe / CPU | 22.2 ms | 10 (15) | 100% | stored session 36: 141 samples, 6 AOI buckets, orientation=portrait | 374 px ≈ 19.6° |
| Try page, SwiftShader "GPU" (desktop) | mediapipe / GPU | 99 ms | 5 (adaptive 6) | 100% | 66, moving | 14.3° |

Every request (`config`, `consent`, `session/start`, `calibrated`, `batch`, `lesson-summary`) returned 200
with CSRF on. In all runs AOI resolution fell back to `heading`, which is correct for a validation
error this large.

### Mobile code paths (`tools/helix_mobile_check.py`, emulated Pixel UA, touch, DPR 3)

- `HelixEngine.isMobile()` = true; the track constraint was `facingMode: "user"`; the video had
  `playsinline` + `webkit-playsinline` + `muted`; the fake camera gave 480×480 @ 15 fps; mobile
  fps cap = 15.
- Positioning guidance passed at ~28 cm. Calibration dots used the `touch` class, and 9 taps → 9 dots.
- Rotate to 844×390: no landscape model existed yet, so a **quick 5-dot** calibration opened. It
  was completed by tapping.
- Rotate back to 390×844: "Rotated: using your portrait calibration". No recalibration ran, and
  31 new estimates followed within 2.5 s.
- This is *emulation*. Real iOS Safari/Android Chrome permission prompts, `orientationchange`
  timing, and thermal behaviour are untested.

## 3. Landmark replay (`node tools/helix_eval/replay.js` → `replay_results.json`)

**Input:** 401 recorded MediaPipe frames (`tests/fixtures/mp_landmarks_face_clip.json`).

**Results:**
- Face detected: 100%
- Median eye width in the image: 38.9 px
- Iris-centre jitter (robust σ after a 5-frame median): **0.03 px**. This is a *lower bound*.
  MediaPipe smooths landmarks over time in VIDEO mode, and this compressed clip has no sensor
  noise. The "predicted at measured noise" number (10 px) is therefore a noise floor, **not an
  accuracy claim**. Expect real webcams to sit nearer the 0.4–1.6 px rows of table 1.
- **Bug found and fixed:** the old fixed rule (`open < 0.13` → blink) threw away **28%** of frames.
  These were runs of up to 2.5 s with `eyeLookDown ≈ 0.8`, meaning she was looking down, not
  blinking. That would have discarded students reading the bottom of the page. The new rule (narrow
  lids count as a blink only if not explained by downward gaze, using blendshapes) rejects **1%**.

## 4. Not verified (needs a real person and real devices)

- True accuracy, measured by a person following the validation dots. The live validation step does
  exactly this and reports px and degrees, so the first real session gives the real number.
- iOS Safari and Android Chrome: getUserMedia/playsinline behaviour, GPU delegate speed,
  thermal/battery throttling, rotation on real hardware.
- WebGL GPU delegate on a real GPU.
- Glasses, low light, darker or lighter skin tones, and multiple faces.

## Pass 4: real-face warp proxy (real MediaPipe on real faces, known targets)

**Why:** the synthetic eval feeds the model ideal landmarks. Here the **real MediaPipe Face
Landmarker (tasks-vision 1.1.1, CPU/WASM, same `HelixEngine._process` code path as the browser)**
runs on real face video whose eyes were re-rendered to look at known screen points.

**Sources (licence-clean, outside the repo in /workspace/ciwt/testdata):** U.S. CBP vlog (public
domain, 1080p; used as 640x480 and 1280x720), Presidential Press and Information Office interview
(CC BY 4.0, 384x288 upscaled), Zara Kay interview (CC0). Datasets with screen targets were checked
and **not used**: MPIIFaceGaze (CC BY-NC-SA), EOTT / WEyeDS (registration). WebQAmGaze (CC BY 4.0)
only has WebGazer outputs (its reported validation offsets of ~65-117 px median are context, not
comparable).

**Warp (tools/helix_eval/warp/gen.py):** per frame, landmarks + head pose are smoothed
(sigma 1.5 frames); the target's eye-in-head angle is computed from a 1440x900 screen (0.0213
cm/px, camera top-centre) at the iris-estimated distance; the iris is removed (sclera fill) and
re-rendered at that angle (4x supersampled), lids follow vertical gaze, iris clipped by the lid
mask. Conditions: clean, webcam (noise + blur + JPEG 55), low light, glasses glare (frame +
specular blob), a second face, partial occlusion (hand / one eye), and "moved" (4 cm + 10 %
closer after calibration, then 12 implicit clicks). Protocol: 9-point calibration (20 frames
each) -> 16 **unseen** validation points (per-point median error), smooth pursuit (Lissajous,
9 s, eye trails 2 frames), reading phase with known fixations.

Run: `run.py features <suffix> <dirs>` (headless Chromium, ~25 ms/frame) then
`node tools/helix_eval/warp/warp_eval.js <suffix> <dirs>`. Full table: warp/RESULTS_v2.md.

| median over 4 sequence sets | baseline engine (pass 3) | pass-4 engine |
|---|---|---|
| 9-point -> 16 unseen points, all 28 sequences | 7.74° | 7.97° |
| held-out subjects only (medvedev, cbp720) | 7.26° | 7.56° |
| clean / webcam / low light / glare | 7.1 / 7.85 / 8.3 / 8.72° | 6.79 / 7.56 / 8.64 / 9.59° |
| second face / occlusion | 7.53 / 7.95° | 7.76 / 8.43° |
| follow-the-dot + 3 dots (what the UI does) | 8.09° | 7.59° |
| follow-the-dot only | 10.19° | 7.41° |
| moved 4 cm + 10 % closer, no clicks -> 12 clicks | 7.68 -> 8.20° | 8.70 -> 8.10° |
| face found | 99-100 % | 99-100 % |

Honest reading of these numbers:
* **About 7-8° median (~300-400 px at 60 cm) is the floor on this proxy**, for every condition.
  Base vs pass-4 differences are within about ±1° and change sign by subject. A deterministic
  A/B of `numFaces` 1 vs 2 moved the medians by a similar amount, so treat sub-1° changes as
  noise. Per subject: cbp720 (1280x720) ~5.7°, cbp ~6.8°, medvedev ~7°, zara 11-15°
  (smallest eyes in frame).
* Diagnostics: MediaPipe's iris landmarks capture only ~40 % of the rendered horizontal iris
  shift and almost none of the vertical; vertical gaze comes from lid openness / blendshapes.
  That limits accuracy no matter which model sits on top. The new blink gate keeps looking-down
  frames (the old rule rejected them) but did not move the medians.
* After head movement the error is mostly **scatter, not offset**: even an oracle bias
  correction barely helps (e.g. cbp 350 -> 356 px). So 12 clicks recover only ~0.6°. Tuning
  head compensation further on this proxy would be fitting noise; the synthetic 4 cm/5° case is
  unchanged (4.09° -> 1.88° after 20 clicks).
* Fixations from reading at this accuracy: I-DT finds 2-16 of 57 true fixations with ~0-33 %
  on the correct line. **Line-level reading is not supported**; heading-level AOIs are what the
  accuracy supports, which matches what `aoiResolution` already chooses.
* Caveats: 3 people, only iris/lids are synthesised (no corneal reflection, no real
  eye-rotation shading), source videos were not looking at a screen, talking and expressions
  are present, and the pose of low-res sources is noisy. Real users at a real screen can be
  better (real eye rotation moves more than the iris disc) or worse (real glare, real fatigue).
  **Nothing here replaces a test with people at a screen.**
