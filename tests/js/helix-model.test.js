// Run: node --test tests/js/
const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const M = require('../../static/js/helix/helix-model.js');
const S = require('../../tools/helix_eval/synth.js');

function feats(u, t, head, extra) {
  const fr = S.frame(u, t, head || u.head, extra);
  return M.eyeFeatures(fr.lm, u.W, u.H, fr.matrix, { hfovDeg: u.hfovDeg });
}
function calibrated(seed, over) {
  const u = S.makeUser(seed, over);
  const reg = new M.GazeRegressor();
  S.grid(u, 3, 3, 0.1).forEach((t) => { for (let k = 0; k < 20; k++) { const f = feats(u, t); if (f && !f.blink) reg.addCalibration(f.vec, t[0], t[1]); } });
  reg.fit();
  return { u, reg };
}
function valErr(u, reg, head) {
  const errs = S.grid(u, 4, 4, 0.14).map((t) => {
    let sx = 0, sy = 0, n = 0;
    for (let k = 0; k < 20; k++) { const f = feats(u, t, head); if (!f || f.blink) continue; const p = reg.predict(f.vec); sx += p.x; sy += p.y; n++; }
    return Math.hypot(sx / n - t[0], sy / n - t[1]);
  }).sort((a, b) => a - b);
  return errs[errs.length >> 1];
}

test('eyeFeatures: 23 named features, sane distance and pose from synthetic landmarks', () => {
  const u = S.makeUser(3);
  const f = feats(u, [720, 450]);
  assert.strictEqual(f.vec.length, M.FEATURE_NAMES.length);
  assert.ok(f.vec.every(Number.isFinite));
  assert.ok(Math.abs(f.distanceCm - u.head.z) < 8, 'distance ' + f.distanceCm + ' vs ' + u.head.z);
  assert.strictEqual(f.blink, false);
  assert.ok(feats(u, [720, 450], null, { blink: true }).blink, 'closed lids are a blink');
});

test('blink rule: narrow lids while looking DOWN are not a blink (MediaPipe blendshapes)', () => {
  const u = S.makeUser(4);
  const fr = S.frame(u, [720, 450], u.head, { blink: 'half' });
  const bs = (blink, down) => [{ categoryName: 'eyeBlinkLeft', score: blink }, { categoryName: 'eyeBlinkRight', score: blink },
    { categoryName: 'eyeLookDownLeft', score: down }, { categoryName: 'eyeLookDownRight', score: down }];
  const f = M.eyeFeatures(fr.lm, u.W, u.H, fr.matrix, { blendshapes: bs(0.6, 0.85) });
  assert.ok(f.open > 0.04 && f.open < 0.13, 'test needs narrow-but-open lids, got ' + f.open);
  assert.strictEqual(f.blink, false, 'downward reading gaze kept');
  assert.strictEqual(M.eyeFeatures(fr.lm, u.W, u.H, fr.matrix, { blendshapes: bs(0.9, 0.1) }).blink, true);
});

test('jacobiEigen reconstructs a symmetric matrix', () => {
  const A = [[4, 1, 0.5], [1, 3, 0.2], [0.5, 0.2, 2]];
  const { d, V } = M.jacobiEigen(A);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    let s = 0; for (let k = 0; k < 3; k++) s += V[i][k] * d[k] * V[j][k];
    assert.ok(Math.abs(s - A[i][j]) < 1e-9);
  }
});

test('hybrid regressor: calibrated synthetic user is accurate to < 3 deg', () => {
  const { u, reg } = calibrated(11);
  const e = valErr(u, reg);
  const deg = M.angularError(e, u.head.z, u.cmPerPx);
  assert.ok(deg < 3, 'median error ' + e.toFixed(0) + ' px = ' + deg.toFixed(2) + ' deg');
  assert.ok(reg.model && reg.model.lambda != null, 'GCV picked a lambda');
});

test('hybrid model survives head movement much better than a single ridge', () => {
  const moved = (u) => Object.assign({}, u.head, { x: u.head.x + 4, yaw: u.head.yaw + 5 * Math.PI / 180 });
  let hybrid = 0, ridge = 0;
  for (const seed of [21, 22, 23]) {
    const a = calibrated(seed); hybrid += valErr(a.u, a.reg, moved(a.u));
    const u = S.makeUser(seed), r = new M.GazeRegressor({ features: M.FEATURE_NAMES.map((_, i) => i) });
    S.grid(u, 3, 3, 0.1).forEach((t) => { for (let k = 0; k < 20; k++) { const f = feats(u, t); if (f && !f.blink) r.addCalibration(f.vec, t[0], t[1]); } });
    r.fit(); ridge += valErr(u, r, moved(u));
  }
  assert.ok(hybrid < ridge * 0.6, 'hybrid ' + hybrid / 3 + ' vs ridge ' + ridge / 3);
});

test('implicit click samples pull a drifted model back (online adaptation)', () => {
  const { u, reg } = calibrated(31);
  const head = Object.assign({}, u.head, { x: u.head.x + 4, yaw: u.head.yaw + 5 * Math.PI / 180 });
  const before = valErr(u, reg, head);
  for (let k = 0; k < 20; k++) {
    const t = [u.r() * u.screenW, u.r() * u.screenH];
    const f = feats(u, t, head); if (f && !f.blink) reg.addImplicit(f.vec, t[0], t[1]);
  }
  reg.fit();
  const after = valErr(u, reg, head);
  assert.ok(after < before * 0.85, 'before ' + before.toFixed(0) + ' after ' + after.toFixed(0));
});

test('OrientationModels keeps one model per orientation', () => {
  const om = new M.OrientationModels();
  om.use('portrait'); assert.strictEqual(om.ready(), false);
  const reg = om.current();
  const { u } = calibrated(5);
  S.grid(u, 3, 3, 0.1).forEach((t) => { const f = feats(u, t); reg.addCalibration(f.vec, t[0], t[1]); reg.addCalibration(f.vec, t[0], t[1]); });
  reg.fit();
  assert.strictEqual(om.ready('portrait'), true);
  om.use('landscape'); assert.strictEqual(om.ready(), false, 'rotating needs its own calibration');
  om.use('portrait'); assert.strictEqual(om.ready(), true);
});

test('poseGuidance flags distance, centring and turning', () => {
  const u = S.makeUser(6);
  u.head = Object.assign({}, u.head, { x: 0, y: 0 });   // face in the middle of the camera image
  const ok = feats(u, [720, 450]);
  const g = M.poseGuidance(ok, { brightness: 120 });
  assert.ok(g.ok, JSON.stringify(g.checks));
  const near = feats(u, [720, 450], Object.assign({}, u.head, { z: 22 }));
  assert.strictEqual(M.poseGuidance(near).checks.find((c) => c.key === 'distance').ok, false);
  assert.strictEqual(M.poseGuidance(near, { mobile: true }).checks.find((c) => c.key === 'distance').ok, true, '22 cm is fine on a phone');
  const turned = feats(u, [720, 450], Object.assign({}, u.head, { yaw: 25 * Math.PI / 180 }));
  assert.strictEqual(M.poseGuidance(turned).checks.find((c) => c.key === 'facing').ok, false);
  assert.strictEqual(M.poseGuidance(ok, { brightness: 20 }).ok, false, 'too dark');
  assert.strictEqual(M.poseGuidance(null).ok, false);
});

test('angularError and aoiResolution', () => {
  assert.ok(Math.abs(M.angularError(96, 60) - Math.atan(2.54 / 60) * 180 / Math.PI) < 1e-9);
  assert.strictEqual(M.angularError(100, null), null);
  assert.strictEqual(M.aoiResolution(15), 'line');
  assert.strictEqual(M.aoiResolution(50), 'paragraph');
  assert.strictEqual(M.aoiResolution(200), 'heading');
  assert.strictEqual(M.aoiResolution(null), 'heading');
  assert.strictEqual(M.aoiResolution(60, { paragraphHeight: 200 }), 'paragraph');
});

test('DriftTracker: median window, drift threshold with 120 px floor, recal marker', () => {
  const d = new M.DriftTracker({ window: 5 });
  [60, 70, 80, 65, 75].forEach((e, i) => d.add(e, i * 1000, 'click'));
  assert.strictEqual(d.median(), 70);
  assert.strictEqual(d.drifting(50), false, 'floor of 120 px');
  [300, 320, 310, 290, 305].forEach((e, i) => d.add(e, 6000 + i * 1000, 'tap'));
  assert.strictEqual(d.drifting(60), true);
  d.reset(12000);
  assert.strictEqual(d.median(), null);
  assert.strictEqual(d.points[d.points.length - 1].src, 'recal');
  assert.strictEqual(d.points.length, 11);
});

// ---------------------------------------------------------------- pass 4 robustness helpers
test('I-DT fixation detector finds fixations and ignores saccade samples', () => {
  const s = []; let t = 0;
  const fix = (x, y, n) => { for (let i = 0; i < n; i++) { s.push({ t, x: x + (i % 3) * 5, y: y + (i % 2) * 5 }); t += 33; } };
  fix(100, 100, 8); s.push({ t, x: 400, y: 120 }); t += 33; fix(700, 140, 9);
  const f = M.detectFixations(s, { method: 'idt', dispersionPx: 60, minMs: 100 });
  assert.strictEqual(f.length, 2);
  assert.ok(Math.abs(f[0].x - 105) < 10 && Math.abs(f[1].x - 705) < 10);
  const v = M.detectFixations(s, { method: 'ivt', velocityPxPerS: 1500, minMs: 100 });
  assert.strictEqual(v.length, 2);
  const d = new M.FixationDetector({ dispersionPx: 60, minMs: 100 });
  let done = 0; s.forEach((p) => { if (d.push(p.t, p.x, p.y)) done++; });
  assert.strictEqual(done, 1); assert.ok(d.current() && Math.abs(d.current().x - 705) < 10);
});

test('BlinkGate: short closure is a blink, sustained narrowing (looking down) is kept', () => {
  const g = new M.BlinkGate(); let t = 0, blinks = 0, kept = 0;
  const f = (open, look) => ({ open, lookDown: look || 0, blinkScore: 0 });
  for (let i = 0; i < 60; i++) { g.update(f(0.3), t); t += 33; }
  for (let i = 0; i < 4; i++) { if (g.update(f(0.01), t)) blinks++; t += 33; }
  for (let i = 0; i < 30; i++) { g.update(f(0.3), t); t += 33; }
  for (let i = 0; i < 40; i++) { if (!g.update(f(0.12, 0.7), t)) kept++; t += 33; }
  assert.strictEqual(blinks, 4); assert.ok(kept >= 35, 'looking-down frames kept: ' + kept);
});

test('fitPursuit recovers the eye lag behind a moving dot', () => {
  const { u } = calibrated(41);
  const path = [], rows = [];
  for (let k = 0; k < 300; k++) {
    const tt = k * 33, s = tt / 1000;
    path.push({ t: tt, x: u.screenW / 2 + 0.4 * u.screenW * Math.sin(2 * Math.PI * s / 4.5), y: u.screenH / 2 + 0.38 * u.screenH * Math.sin(2 * Math.PI * s / 3 + 0.6) });
  }
  for (let k = 5; k < 300; k++) {   // eye trails the dot by 5 frames (165 ms)
    const f = feats(u, [path[k - 5].x, path[k - 5].y]); if (f && !f.blink) rows.push({ t: path[k].t, vec: f.vec });
  }
  const fit = M.fitPursuit(rows, path);
  assert.ok(fit && Math.abs(fit.lag - 165) <= 40, 'lag ' + (fit && fit.lag));
});

test('recalTrigger fires on distance and head-turn changes, not on small moves', () => {
  const base = { distanceCm: 60, yaw: 0, pitch: 0, faceX: 0.5, faceY: 0.5 };
  assert.strictEqual(M.recalTrigger(base, Object.assign({}, base, { distanceCm: 63, yaw: 0.05 })), null);
  assert.strictEqual(M.recalTrigger(base, Object.assign({}, base, { distanceCm: 44 })).reason, 'distance');
  assert.strictEqual(M.recalTrigger(base, Object.assign({}, base, { yaw: 0.25 })).reason, 'head_turn');
});

test('cleanCalibrationSamples trims tap-shake and early-saccade outlier frames and produces a clean anchor', () => {
  const { u } = calibrated(51);
  const samples = [];
  for (let i = 0; i < 12; i++) {
    samples.push(feats(u, [500, 400]));
  }
  // Add 1 blink frame, 1 tap-shake frame (large pose jump), and 3 early-saccade outlier frames looking at [1200, 750]
  const blinkF = feats(u, [500, 400]); blinkF.blink = true; samples.push(blinkF);
  const shakeF = feats(u, [500, 400]); shakeF.pose = { yaw: shakeF.pose.yaw + 0.12, pitch: shakeF.pose.pitch + 0.08, roll: 0 }; samples.push(shakeF);
  for (let i = 0; i < 3; i++) samples.push(feats(u, [1200, 750]));

  const cleaned = M.cleanCalibrationSamples(samples);
  assert.ok(cleaned.dropped >= 4, 'dropped blink, shake, and saccade outliers: ' + cleaned.dropped);
  assert.ok(cleaned.kept.length >= 8 && cleaned.kept.length <= 13, 'kept clean majority: ' + cleaned.kept.length);
  assert.ok(Array.isArray(cleaned.anchor) && cleaned.anchor.length === 23, 'anchor vector produced');
});

test('fuseCropFeatures blends plausible crop pupil centers into iris features and ignores wild glitches', () => {
  const { u } = calibrated(61);
  const f = feats(u, [640, 400]);
  const origUR = f.vec[2], origVR = f.vec[3];
  const crop = {
    r: { tb: [origUR + 0.04, origVR - 0.03], dc: [origUR + 0.04, origVR - 0.03], open: 0.25, upper: -0.12, lower: 0.13, patch: [] },
    l: { tb: [f.vec[4] + 0.04, f.vec[5] - 0.03], dc: [f.vec[4] + 0.04, f.vec[5] - 0.03], open: 0.25, upper: -0.12, lower: 0.13, patch: [] }
  };
  const cvec = M.fuseCropFeatures(f, crop);
  assert.strictEqual(cvec.length, 8);
  assert.ok(Math.abs(f.vec[2] - (0.65 * origUR + 0.35 * (origUR + 0.04))) < 1e-6, 'uR fused with crop tb');

  // Wild glitch (> 0.18 away) should not corrupt uR
  const f2 = feats(u, [640, 400]);
  const uR2 = f2.vec[2];
  M.fuseCropFeatures(f2, { r: { tb: [uR2 + 0.45, 0], dc: null, open: 0.25, upper: -0.1, lower: 0.1, patch: [] }, l: null });
  assert.strictEqual(f2.vec[2], uR2, 'implausible crop glitch ignored');
});

test('decoupled lambdaX/lambdaY and Huber IRLS resist corrupted calibration samples', () => {
  const { u, reg } = calibrated(71);
  assert.ok(reg.model.lambdaX != null && reg.model.lambdaY != null, 'lambdaX and lambdaY exposed');
  // Inject 2 wildly corrupted calibration samples (e.g. user looked away during a dot)
  const badF = feats(u, [100, 100]);
  reg.addCalibration(badF.vec, 1250, 780, 1, 99);
  reg.addCalibration(badF.vec, 1250, 780, 1, 99);
  reg.fit();
  const errs = [];
  for (let i = 0; i < 16; i++) {
    const gx = (0.15 + 0.7 * (i % 4) / 3) * u.screenW, gy = (0.15 + 0.7 * Math.floor(i / 4) / 3) * u.screenH;
    const ps = Array.from({ length: 10 }, () => reg.predict(feats(u, [gx, gy]).vec));
    const px = ps.reduce((a, b) => a + b.x, 0) / ps.length, py = ps.reduce((a, b) => a + b.y, 0) / ps.length;
    errs.push(Math.hypot(px - gx, py - gy));
  }
  errs.sort((a, b) => a - b);
  assert.ok(errs[errs.length >> 1] < 95, 'Huber-reweighted median error remains low despite outliers: ' + errs[errs.length >> 1]);
});

test('MediaPipeEngine exportCalibration and importCalibration round-trip via sessionStorage', () => {
  const vm = require('node:vm'), fs = require('node:fs');
  const store = {};
  const ctx = {
    window: {
      HelixModel: M,
      innerWidth: 1280,
      innerHeight: 800,
      matchMedia: () => ({ matches: false }),
      performance: { now: () => Date.now() }
    },
    screen: { width: 1280, height: 800 },
    navigator: { userAgent: 'Mozilla/5.0', hardwareConcurrency: 8 },
    location: { search: '' },
    sessionStorage: {
      getItem: (k) => store[k] || null,
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; }
    },
    WebAssembly: WebAssembly,
    Date: Date, Math: Math, Array: Array, Object: Object, JSON: JSON, Error: Error, Promise: Promise
  };
  ctx.window.sessionStorage = ctx.sessionStorage;
  vm.runInNewContext(fs.readFileSync('static/js/helix/helix-engine.js', 'utf8'), ctx);
  const E = ctx.window.HelixEngine;
  const eng1 = new E.MediaPipeEngine({ mobile: false });
  const { u } = calibrated(81);
  // Feed 9 dots through beginSample / endSample
  const pts = [[150, 100], [640, 100], [1130, 100], [150, 400], [640, 400], [1130, 400], [150, 700], [640, 700], [1130, 700]];
  pts.forEach(([x, y]) => {
    eng1.beginSample(x, y, 1);
    eng1.collect.from = 0;
    for (let i = 0; i < 10; i++) eng1.collect.samples.push(feats(u, [x, y]));
    eng1.endSample();
  });
  assert.strictEqual(eng1.fit(), true, 'eng1 fitted');
  assert.strictEqual(eng1.saveSessionCalibration({ valid: true, score: 86, errorPx: 48 }), true, 'saved to sessionStorage');
  assert.ok(E.getSessionCalibration('landscape'), 'getSessionCalibration returns saved payload');

  // Restore into a brand-new engine instance
  const eng2 = new E.MediaPipeEngine({ mobile: false });
  assert.strictEqual(eng2.ready(), false);
  assert.strictEqual(eng2.loadSessionCalibration('landscape'), true, 'restored calibration');
  assert.strictEqual(eng2.ready(), true);
  assert.strictEqual(eng2.calScore.errorPx, 48);
  const fTest = feats(u, [640, 400]);
  const p1 = eng1.models.current().predict(fTest.vec);
  const p2 = eng2.models.current().predict(fTest.vec);
  assert.ok(Math.hypot(p1.x - p2.x, p1.y - p2.y) < 1e-6, 'restored model predicts identically');
});
