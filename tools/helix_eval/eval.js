#!/usr/bin/env node
/* Repeatable offline accuracy evaluation of the Helix gaze pipeline.
   usage: node tools/helix_eval/eval.js [--users 40] [--json out.json]
   Protocol mirrors the runtime: 9-point calibration (~22 frames per point after the saccade),
   then validation on a 4x4 grid of unseen targets (~22 frames each); error = distance between the
   target and the mean estimate over the point (what the live validation step shows), plus
   per-frame error (what an AOI hit-test sees). Degrees use the simulated viewing distance. */
'use strict';
const path = require('path');
const M = require(path.join(__dirname, '../../static/js/helix/helix-model.js'));
const S = require('./synth.js');
const Core = require(path.join(__dirname, '../../static/js/helix/helix-core.js'));

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const USERS = +opt('users', 40);
const FRAMES = 22;
const NOISE = opt('noise', null), ONLY = opt('only', null);

function median(a) { const s = a.slice().sort((x, y) => x - y); const h = s.length >> 1; return s.length % 2 ? s[h] : (s[h - 1] + s[h]) / 2; }
function mean(a) { return a.reduce((s, v) => s + v, 0) / a.length; }
function pct(a, p) { const s = a.slice().sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(p * s.length))]; }

function feats(u, target, head, extra) {
  const fr = S.frame(u, target, head, extra);
  return M.eyeFeatures(fr.lm, u.W, u.H, fr.matrix, { hfovDeg: u.hfovDeg });
}

function runUser(seed, cond) {
  const u = S.makeUser(seed, cond.user);
  const reg = new M.GazeRegressor({ features: cond.features });
  const calPts = S.grid(u, 3, 3, 0.1);
  let blinksSkipped = 0;
  calPts.forEach((t) => {
    for (let k = 0; k < FRAMES; k++) {
      const blink = u.r() < 0.03;
      const f = feats(u, t, u.head, { blink });
      if (!f || f.blink) { blinksSkipped++; continue; }   // runtime drops blink frames the same way
      reg.addCalibration(f.vec, t[0], t[1]);
    }
  });
  reg.fit();
  const head = Object.assign({}, u.head, cond.headShift || {});
  if (cond.implicit) {          // implicit click samples at random positions after the head moved
    for (let k = 0; k < cond.implicit; k++) {
      const t = [u.r() * u.screenW, u.r() * u.screenH];
      const f = feats(u, t, head);
      if (f && !f.blink) reg.addImplicit(f.vec, t[0], t[1]);
      reg.fit();
    }
  }
  const val = S.grid(u, 4, 4, 0.14);
  const pointErr = [], frameErr = [], smoothErr = [];
  let dist = [];
  val.forEach((t) => {
    const est = [];
    const filt = new Core.GazeFilter({ bounds: { w: u.screenW, h: u.screenH } });
    for (let k = 0; k < FRAMES + 8; k++) {
      const f = feats(u, t, head);
      if (!f || f.blink) continue;
      const p = reg.predict(f.vec);
      const sm = filt.push(p.x, p.y);
      if (k < 8) continue;            // the runtime also discards the first ~250 ms after a saccade
      est.push(p); dist.push(f.distanceCm);
      frameErr.push(Math.hypot(p.x - t[0], p.y - t[1]));
      if (sm.ok) smoothErr.push(Math.hypot(sm.x - t[0], sm.y - t[1]));
    }
    const mx = mean(est.map((p) => p.x)), my = mean(est.map((p) => p.y));
    pointErr.push(Math.hypot(mx - t[0], my - t[1]));
  });
  const trueD = head.z;
  const toDeg = (px) => Math.atan(px * u.cmPerPx / trueD) * 180 / Math.PI;
  return { pointErr, frameErr, smoothErr, smoothDeg: smoothErr.map(toDeg), pointDeg: pointErr.map(toDeg), frameDeg: frameErr.map(toDeg),
    distEstErr: mean(dist) - Math.hypot(trueD, head.y), lambda: reg.model.lambda };
}

const CONDITIONS = [
  { name: 'baseline (noise 0.8 px, head still)', },
  { name: 'ablation: single ridge on all features', features: Array.from({ length: 23 }, (_, i) => i) },
  { name: 'ablation: iris offsets only (no geometry / head pose)', features: [2, 3, 4, 5, 10, 11, 12] },
  { name: 'low landmark noise (0.4 px)', user: { lmNoisePx: 0.4 } },
  { name: 'high landmark noise (1.6 px)', user: { lmNoisePx: 1.6 } },
  { name: 'phone-like: 30 cm, small screen 390x844', user: { distanceCm: 30, screenW: 390, screenH: 844, cmPerPx: 0.0175, head: null } },
  { name: 'head moved 4 cm sideways + 5° yaw after calibration', headShift: null, shift: { dx: 4, dyaw: 5 } },
  { name: '... same, after 20 implicit click samples', shift: { dx: 4, dyaw: 5 }, implicit: 20 },
  { name: 'ablation (single ridge): head moved 4 cm + 5° yaw', shift: { dx: 4, dyaw: 5 }, features: Array.from({ length: 23 }, (_, i) => i) },
  { name: 'head leaned 8 cm closer after calibration', shift: { dz: -8 } },
];

if (NOISE) CONDITIONS.forEach((c) => { c.user = Object.assign({}, c.user || {}, { lmNoisePx: +NOISE }); if (!/noise/.test(c.name)) c.name += ' @ ' + NOISE + ' px noise'; });
const out = [];
for (const c of CONDITIONS.filter((c) => !ONLY || c.name.startsWith(ONLY))) {
  const pE = [], fE = [], pD = [], fD = [], dE = [], sE = [], sD = [];
  for (let s = 1; s <= USERS; s++) {
    const cond = Object.assign({}, c);
    if (c.user && c.user.distanceCm) {
      const base = S.makeUser(s);
      cond.user = Object.assign({}, c.user, { head: Object.assign({}, base.head, { z: c.user.distanceCm + (base.head.z - 55) * 0.4, y: 3 + (base.head.y - 6) * 0.5 }) });
    }
    if (c.shift) {
      const base = S.makeUser(s);
      cond.headShift = { x: base.head.x + (c.shift.dx || 0), z: base.head.z + (c.shift.dz || 0), yaw: base.head.yaw + (c.shift.dyaw || 0) * Math.PI / 180 };
    }
    const r = runUser(1000 + s, cond);
    sE.push(median(r.smoothErr)); sD.push(median(r.smoothDeg));
    pE.push(median(r.pointErr)); fE.push(median(r.frameErr)); pD.push(median(r.pointDeg)); fD.push(median(r.frameDeg)); dE.push(r.distEstErr);
  }
  const row = {
    condition: c.name, users: USERS,
    point_error_px_median: Math.round(median(pE)), point_error_px_p90: Math.round(pct(pE, 0.9)),
    point_error_deg_median: +median(pD).toFixed(2), frame_error_px_median: Math.round(median(fE)),
    frame_error_deg_median: +median(fD).toFixed(2), smoothed_error_px_median: Math.round(median(sE)), smoothed_error_deg_median: +median(sD).toFixed(2), distance_estimate_bias_cm: +mean(dE).toFixed(1)
  };
  out.push(row);
}
const jsonPath = opt('json', null);
if (jsonPath) require('fs').writeFileSync(jsonPath, JSON.stringify({ generated: new Date().toISOString(), frames_per_point: FRAMES, results: out }, null, 2));
const hdr = ['condition', 'users', 'point err px (median / p90)', 'point err °', 'raw frame err px', 'raw frame °', 'smoothed frame err px', 'smoothed °', 'distance bias cm'];
console.log('| ' + hdr.join(' | ') + ' |\n|' + hdr.map(() => '---').join('|') + '|');
out.forEach((r) => console.log('| ' + [r.condition, r.users, r.point_error_px_median + ' / ' + r.point_error_px_p90, r.point_error_deg_median, r.frame_error_px_median, r.frame_error_deg_median, r.smoothed_error_px_median, r.smoothed_error_deg_median, r.distance_estimate_bias_cm].join(' | ') + ' |'));
