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

## Pass 5: high-resolution eye crop, pupil localisation, eye patches, per-user CV (Oct 17 2026)

**Question:** can a second-stage, full-camera-resolution eye crop beat the ~7-8° floor on the warp
proxy? **Answer: not consistently.** Some variants are about 0.2-0.45° better on average, but none
improves every subject *and* repeats across seeds. The default model is therefore **unchanged** from
pass 4. The crop stage ships view-only (Try-page HUD) plus an opt-in experimental model path.

### What was built (all in the real browser path, `HelixEngine._process`)
* `HelixModel.eyeCropTransform`: per eye, a 90x54 crop drawn from the **full-resolution video**,
  rotated so the eye-corner line (33/133, 362/263) is level and scaled to 1/1.5 of the crop width
  (pose-normalised in roll and scale). Face detection input is unchanged.
* Pupil centre in the crop: `pupilTimmBarth` (Timm & Barth 2011 gradient method, restricted to the
  lid polygon, darkness-weighted, coarse step 2 + full-res refinement, ≤400 gradients) and
  `pupilDarkCentroid`. Lid cues: upper/lower lid height where the centre line crosses the lid
  contour. Appearance: `eyePatch` (15x9 area-average, rank-equalised).
* `GazeRegressor`: when vec carries the 8 crop values (pupil x/y per eye from Timm & Barth with
  dark-centroid fallback, plus upper/lower lid per eye), stage 2 uses them, with lambda chosen by
  **grouped CV** (leave-one-calibration-dot-out, 3x3 target grid) instead of per-frame GCV.
  Missing values (NaN, or the stage switching off mid-session) count as the mean.
* Engine: `opts.crop = 'view'` (HUD only), `true` (features into the model, experimental), or off
  (default). Phones run it only when forced. It turns itself off if inference + crop drops below
  ~12 fps. `hiRes` / `?hires=1` requests 1920x1080 on desktops with ≥8 cores, and `_resCheck`
  drops to 720p if inference + crop exceeds 50 ms.

### Data
Pass-4 warp sequences (cbp 640x480, cbp720, medvedev, zara × 7 conditions), plus **cbp1080**: the
same frames as cbp720 at native 1920x1080, all 7 conditions. **Seed repeats:** clean and webcam
re-rendered with seeds 1 and 2 (different noise and target order) for all 5 subjects. That gives
55 sequences in total. Features were dumped once with the crop stage on (`run.py features _v5`) and
A/B'd offline with `crop_ab.js`. The ported model was scored with `warp_eval.js` on the same dumps
(`CROPVEC=0` gives the pass-4 model on identical frames).

**Resolution note:** at 640x480/720p the eye crop *upsamples* (median 0.34-0.72 camera px per crop
px; MediaPipe's own ~256 px face crop already sees about native resolution). Only at 1080p does
the crop get real extra detail (1.07 px/px). So at ≤720p the crop adds a different estimator, not
new pixels.

### Offline A/B, 9-point → 16 unseen points (median per-point error, °; `crop_ab.js`)
| variant (stage-2 features, lambda) | all 55 | mean Δ vs pass-4 [95% CI] | wins | sign p | subjects better, 7 conditions | subjects better, seeds | main 28 | seeds 20 |
|---|---|---|---|---|---|---|---|---|
| pass-4 model (GCV) | 7.53 | — | — | — | — | — | 7.97 | 6.87 |
| + grouped-CV lambda only | 7.22 | -0.21 [-0.55, +0.09] | 30/55 | 0.59 | 3/5 | 3/5 | 7.69 | 6.96 |
| + Timm & Barth pupil, CV | 7.17 | -0.29 [-0.60, +0.01] | 35/55 | 0.06 | 4/5 | 3/5 | 7.58 | 6.53 |
| + lids, CV | 7.27 | -0.16 [-0.52, +0.17] | 30/55 | 0.59 | 3/5 | 2/5 | 7.67 | 6.96 |
| + pupil + lids, CV (= experimental port) | 7.17 | -0.24 [-0.57, +0.10] | 34/55 | 0.11 | 4/5 | 3/5 | 7.75 | 6.59 |
| + pupil + lids, GCV | 7.58 | -0.04 [-0.32, +0.23] | 27/55 | 1.00 | 2/5 | 3/5 | 8.09 | 6.53 |
| + 10x6 patches, PCA 12, CV | 7.12 | -0.37 [-0.72, -0.05] | 37/55 | 0.014 | 3/5 | 5/5 | 7.57 | 6.11 |
| + 5x3 patches, CV | 7.31 | -0.41 [-0.76, -0.07] | 37/55 | 0.014 | 3/5 | 4/5 | 7.58 | 6.07 |
| + pupil + lids + patches PCA 12, CV | 6.99 | -0.45 [-0.76, -0.16] | 37/55 | 0.014 | 4/5 | 4/5 | 7.59 | 6.02 |
| per-user choice by CV (base / pupil+lids / patches) | 7.12 | -0.35 [-0.68, -0.04] | 37/55 | 0.014 | 3/5 | 5/5 | 7.73 | 6.11 |

The best combination still makes **cbp (640x480) 1.2° worse** over its 7 conditions
(7.53 → 8.74). Patches alone make cbp and cbp1080 worse over theirs. The seed-1 and seed-2 results
disagree for cbp720 and medvedev. Median vertical error moves 4.74 → 4.36-4.46° with the pupil
features (patches: no vertical gain). An earlier run that A/B'd a less robust lid definition showed
"-0.36°, p=0.03" for pupil+lids; after fixing the lid computation (no missing values) that shrank
to the -0.24° above. That alone shows how fragile these effects are.

### Ported experimental model through the real engine (`crop: true`; warp_eval, 9-point unless noted)
| set | pass-4 model | pass-5 crop model | wins | mean Δ [95% CI] |
|---|---|---|---|---|
| main 28 | 7.97° | 7.75° | 19/28 | -0.28 [-0.82, +0.22] |
| held-out subjects (medvedev, cbp720) | 7.56° | 7.18° | 9/14 | -0.09 |
| seed repeats (20) | 6.87° | 6.58° | 11/20 | -0.08 |
| cbp1080 (7) | 7.02° | 6.63° | 4/7 | -0.38 |
| all 55 | 7.53° | 7.19° | 34/55 (p=0.11) | -0.22 [-0.55, +0.13] |
| all 55, follow-the-dot + 3 dots | 7.03° | 7.29° | 20/50 | **+0.20 (worse)** |
| moved, no clicks → after 12 clicks (5) | 8.83 → 7.39° | 8.57 → 7.89° | | |

| subject (9-point) | clean | 7 conditions | seeds (4) |
|---|---|---|---|
| cbp (640x480) | 6.86 → 7.02 | 7.53 → **8.48** | 6.35 → 6.50 |
| cbp720 | 5.83 → 5.61 | 7.54 → 7.08 | 6.42 → 5.96 |
| cbp1080 | 5.90 → 5.18 | 7.02 → 6.63 | 5.28 → 5.07 |
| medvedev | 6.72 → 6.33 | 7.58 → 7.20 | 7.98 → 7.94 |
| zara | 11.54 → 10.63 | 10.84 → 10.03 | 9.93 → 9.99 |

### Camera resolution (same person, same frames; pass-4 model)
cbp1080 vs cbp720 over 11 paired sequences: 9-point 6.91 → 6.54° (better in 7/11, mean -0.33°,
p=0.55); **follow-the-dot + 3 dots 6.22 → 5.28° (better in 9/10, p=0.02)**. Only one subject has
a 1080p source, so 1080p is opt-in (`hiRes`), not the default. 480p crop → 720p: 6.86 → 6.91° (no
change).

### CPU cost (headless Chromium, CPU/WASM delegate, this box, one job at a time)
| input | MediaPipe inference | crop stage, Timm & Barth + centroid (both eyes) | crop stage, centroid only |
|---|---|---|---|
| 640x480 desktop | 24.0 ms/frame | +2.0 ms | +0.7 ms |
| 1280x720 desktop | 29.0 ms | +2.3 ms | +0.8 ms |
| 1920x1080 desktop | 39.9 ms (36.3 ms with detection on a 1280-wide copy) | +2.4 ms | +0.8 ms |
| phone emulation (mobile flag, 640x480) | 25.9 ms | off by default; forced centroid-only +0.7 ms | |
| Try page, fake 1280x720 camera (e2e) | 17-35 ms | +3.3-4.2 ms (view only) | |
Timm & Barth alone on a synthetic 90x54 crop in node: 18 ms at full resolution → 4.9 ms with
coarse-to-fine. "Phone emulation" is the desktop CPU with the mobile code path; it is not a phone
measurement.

### Limitations of this proxy for these questions
* The warp moves the iris and the lids (upper lid 75 %, lower lid 25 % of the iris travel), so
  vertical lid cues are measurable. It has **no eyeball shading change, no corneal reflection and
  no limbus foreshortening**. Appearance (patch) features may therefore be under- or over-rated
  here compared with real eyes.
* 3 people (5 resolution variants); seed repeats reuse the same source frames. Effects of 0.2-0.5°
  are inside the run-to-run spread seen in pass 4.
* Pose normalisation of the crop (roll + scale) is built in and was not ablated separately,
  because the features it serves were not adopted.

## Pass 10: second 1080p subject, follow-the-dot, per-device defaults

### New data (outside the repo, /workspace/ciwt/testdata)
**blk1080 / blk720:** U.S. Department of State video "Secretary Blinken on Mahsa Amini's death a year
ago in Iran" (Wikimedia Commons, `File:Secretary Blinken on Mahsa Amini's death a year ago in Iran.webm`,
public domain as a work of the U.S. federal government), 1920x1080. 150 frames at 15 fps from 0:12;
blk720 is the same frames area-scaled to 1280x720. Face found in 150/150. Warped with `gen.py` into the
same 7 conditions plus seeds 1 and 2 for clean and webcam (11 sequences per resolution), features
`run.py features _v5`, scored with `CROPVEC=0 warp_eval.js` (pass-4 model, the shipped default). The
cbp pair was re-scored in the same run. Rejected candidates: ISS videos (faces too small) and further
CBP vlog days (same presenter as cbp, or two people in frame).

### 1080p vs 720p (same person, same frames; median of 16 unseen points per sequence, °)
| subject | 9-point | follow + 3 dots | follow only |
|---|---|---|---|
| blk (11 / 10 / 10 pairs) | 2.82 → 2.82, better 6/11, p=1.0 | 2.67 → 2.40, better 7/10, p=0.34 | 2.93 → 2.75, better 9/10, p=0.02 |
| cbp (re-run, same as pass 5) | 6.91 → 6.54, better 7/11, p=0.55 | 6.22 → 5.28, better 9/10, p=0.02 | 5.71 → 5.39, better 7/10, p=0.34 |
| both, sequence-level | mean −0.27°, 13/22, p=0.52 | mean −0.46°, 16/20, p=0.012 | mean −0.37°, 16/20, p=0.012 |

Read carefully: the sign test across sequences treats the 10–11 sequences of one person as
independent, which they are not (same frames, different synthetic conditions and seeds). At the
level that matters, people, the evidence is **2 of 2 subjects** improving with 1080p for
follow-the-dot calibration, by 0.27° (blk) and 0.94° (cbp) in the median. Neither subject is a real
webcam: both are studio/press video with good lighting, so the 1080p advantage on a real laptop
camera (more noise, compression, worse optics) is unknown. Cost on this box: MediaPipe inference
48 ms vs 33 ms per frame (median; the box was heavily loaded by other jobs during this run, so the
absolute numbers are high, the ratio matches pass 5).

### Follow-the-dot + 3 dots vs 9 dots (same sequences)
| subject | 9-point | follow + 3 | follow better |
|---|---|---|---|
| blk720 | 2.75 | 2.67 | 7/10, p=0.34 |
| blk1080 | 2.76 | 2.40 | 5/10, p=1.0 |
| cbp720 | 7.00 | 6.22 | 7/10, p=0.34 |
| cbp1080 | 6.22 | 5.28 | 8/10, p=0.11 |
Follow+3 is never worse in the median, but no subject shows a significant difference, and the
proxy has no click-timing or attention lapses, which is exactly where the two methods differ for
real people (following a dot needs sustained attention; clicking gives a guaranteed fixation).

### Decision: defaults per device class (unchanged, and why)
| device class | method | camera | basis |
|---|---|---|---|
| desktop | dots (follow offered in positioning) | 1280x720; 1080p opt-in (`hiRes`, ≥8 cores) | 2 proxy subjects, not real webcams; +45% CPU per frame |
| tablet | dots | 1280x720 | no tablet data at all |
| phone | dots | 480x640 portrait | no phone data; 1080p never offered |
Rule adopted for changing a default: real paired data from the accuracy study (`/helix/study`,
admin view `/admin/helix/accuracy`) with at least 10 people who did both arms on that device class,
sign test p < 0.05 and a median gain of at least 0.5°. The admin view applies this rule and shows a
suggestion; an admin changes the default by hand (`HelixCalibDefault`, served in `/api/helix/config`).
Until then the proxy result above is a reason to run the study arms, not to switch.

### Real-device accuracy: still none
The accuracy-study mode is built and tested end to end with a fake camera (the e2e deletes its own
records because a looping video has no gaze ground truth). No real-user numbers exist yet; the
admin view says so instead of showing proxy or seeded numbers.
