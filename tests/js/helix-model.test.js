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
