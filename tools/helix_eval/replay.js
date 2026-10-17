#!/usr/bin/env node
/* Replay a landmark stream recorded from MediaPipe Face Landmarker on a real face video
   (tools/helix_mp_e2e.py --record) through the Helix feature extractor and report what can be
   measured honestly without ground-truth gaze: detection rate, inference time, distance/pose,
   and landmark jitter (the noise that limits accuracy). The measured jitter is then fed into the
   synthetic simulator (synth.js) to predict accuracy at that real noise level.
   usage: node tools/helix_eval/replay.js [fixture.json] [--json out.json] */
'use strict';
const fs = require('fs'), path = require('path');
const M = require(path.join(__dirname, '../../static/js/helix/helix-model.js'));
const args = process.argv.slice(2);
const file = args.find((x) => x.endsWith('.json') && args[args.indexOf(x) - 1] !== '--json') || path.join(__dirname, '../../tests/fixtures/mp_landmarks_face_clip.json');
const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const W = 640, H = 480;
const med = (a) => { const s = a.slice().sort((x, y) => x - y); const h = s.length >> 1; return s.length ? (s.length % 2 ? s[h] : (s[h - 1] + s[h]) / 2) : null; };
const mad = (a) => { const m = med(a); return med(a.map((v) => Math.abs(v - m))); };

const frames = data.frames;
// the fake camera plays 15 fps while detection may run on repeated frames: drop exact duplicates
let prevKey = null, dupes = 0;
const faces = frames.filter((f) => {
  if (!f.face) return false;
  const k = f.lm[468].join(',') + '|' + f.lm[473].join(',');
  if (k === prevKey) { dupes++; return false; }
  prevKey = k; return true;
});
const feats = faces.map((f) => {
  const lm = new Array(478); Object.keys(f.lm).forEach((k) => { lm[+k] = { x: f.lm[k][0], y: f.lm[k][1], z: 0 }; });
  const bs = f.blinkScore == null ? null : [
    { categoryName: 'eyeBlinkLeft', score: f.blinkScore }, { categoryName: 'eyeBlinkRight', score: f.blinkScore },
    { categoryName: 'eyeLookDownLeft', score: f.lookDown }, { categoryName: 'eyeLookDownRight', score: f.lookDown }];
  return M.eyeFeatures(lm, W, H, null, { blendshapes: bs });
}).filter(Boolean);

// jitter: residual of each signal after a 5-frame running median (removes real eye/head motion)
function jitter(sig) {
  const res = [];
  for (let i = 2; i < sig.length - 2; i++) res.push(sig[i] - med(sig.slice(i - 2, i + 3)));
  return 1.4826 * mad(res);   // robust sigma
}
const irisPx = (fr, a, b, c) => { const l = fr.lm; return [l[a][0] * W - (l[b][0] + l[c][0]) / 2 * W, l[a][1] * H - (l[b][1] + l[c][1]) / 2 * H]; };
const rx = faces.map((f) => irisPx(f, 468, 33, 133)[0]), ry = faces.map((f) => irisPx(f, 468, 33, 133)[1]);
const lx = faces.map((f) => irisPx(f, 473, 362, 263)[0]), ly = faces.map((f) => irisPx(f, 473, 362, 263)[1]);
const sigmaPx = med([jitter(rx), jitter(ry), jitter(lx), jitter(ly)]);
const uJ = jitter(feats.map((f) => (f.eyes.r.u + f.eyes.l.u) / 2)), vJ = jitter(feats.map((f) => (f.eyes.r.v + f.eyes.l.v) / 2));
const eyeW = med(feats.map((f) => f.eyes.r.width));
const infer = frames.map((f) => f.infer).filter((x) => x != null);
const out = {
  source: data.meta, frames: frames.length, face_detected_pct: Math.round(100 * faces.length / frames.length),
  inference_ms_median: +(med(infer) || 0).toFixed(1),
  distance_cm_median: Math.round(med(feats.map((f) => f.distanceCm))),
  yaw_deg_range: [Math.round(Math.min(...faces.map((f) => f.pose.yaw)) * 57.3), Math.round(Math.max(...faces.map((f) => f.pose.yaw)) * 57.3)],
  eye_width_px_median: +eyeW.toFixed(1),
  iris_jitter_sigma_px: +sigmaPx.toFixed(2),
  iris_offset_jitter_u: +uJ.toFixed(4), iris_offset_jitter_v: +vJ.toFixed(4),
  duplicate_frames_dropped: dupes, unique_face_frames: faces.length,
  note: 'MediaPipe applies its own temporal smoothing in VIDEO mode, so this jitter is a lower bound on per-frame noise; real webcams add sensor noise and motion blur that this compressed video may not have.',
  blink_frames_pct_naive_threshold: Math.round(100 * faces.filter((f) => f.open < 0.13).length / faces.length),
  blink_frames_pct: Math.round(100 * feats.filter((f) => f.blink).length / feats.length)
};
// predicted accuracy at the measured landmark noise (synthetic, same protocol as eval.js)
const { execFileSync } = require('child_process');
const tmp = path.join(require('os').tmpdir(), 'hx-noise.json');
const synthOut = execFileSync('node', [path.join(__dirname, 'eval.js'), '--users', '30', '--noise', String(out.iris_jitter_sigma_px), '--only', 'baseline', '--json', tmp]).toString();
const synth = JSON.parse(fs.readFileSync(tmp, 'utf8')).results[0];
out.predicted_at_measured_noise = { point_error_px: synth.point_error_px_median, point_error_deg: synth.point_error_deg_median, smoothed_frame_error_px: synth.smoothed_error_px_median, smoothed_frame_error_deg: synth.smoothed_error_deg_median };
const jp = args.indexOf('--json'); if (jp >= 0) fs.writeFileSync(args[jp + 1], JSON.stringify(out, null, 2));
console.log(JSON.stringify(out, null, 2));
