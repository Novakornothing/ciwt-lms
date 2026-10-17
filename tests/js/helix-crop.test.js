'use strict';
/* Pass 5: second-stage eye crop (pose-normalised crop, pupil localisation, lid cues) and the
   crop-aware regressor (missing-value handling, grouped-CV lambda). */
const test = require('node:test');
const assert = require('node:assert');
const M = require('../../static/js/helix/helix-model.js');

function synthEye(ix, iy, opts) {   // 90x54 crop: skin, almond eye opening, dark iris at (ix, iy)
  opts = opts || {}; const W = 90, H = 54, g = new Float32Array(W * H); let s = 7;
  const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const inEye = ((x - 45) / 30) ** 2 + ((y - 27) / (opts.open || 12)) ** 2 < 1, iris = Math.hypot(x - ix, y - iy) < 8.5;
    g[y * W + x] = (!inEye ? 140 : iris ? 45 : 205) + (rnd() - 0.5) * 16;
  }
  const poly = []; for (let k = 0; k < 16; k++) { const a = k / 16 * 2 * Math.PI; poly.push([45 + 30 * Math.cos(a), 27 + (opts.open || 12) * Math.sin(a)]); }
  return { g, W, H, poly };
}

test('eyeCropTransform maps the eye corners onto a level line centred in the crop', () => {
  const A = [300, 210], B = [340, 200];           // tilted eye, 41 px wide
  const T = M.eyeCropTransform(A, B);
  const a = T.apply(A), b = T.apply(B);
  assert.ok(Math.abs(a[1] - b[1]) < 1e-6, 'corner line is horizontal');
  assert.ok(Math.abs((a[0] + b[0]) / 2 - M.CROP.W / 2) < 1e-6 && Math.abs(a[1] - M.CROP.H / 2) < 1e-6, 'centred');
  assert.ok(Math.abs((b[0] - a[0]) - M.CROP.W / M.CROP.SPAN) < 1e-6, 'eye width = W / span');
  const T2 = M.eyeCropTransform(B, A); assert.deepStrictEqual(T2.apply(A).map(Math.round), a.map(Math.round), 'corner order does not matter');
});

test('Timm & Barth and dark-centroid pupil estimates find a synthetic iris within ~1 px', () => {
  for (const [ix, iy] of [[45, 27], [58, 29], [33, 24]]) {
    const e = synthEye(ix, iy), m = M.polygonMask(e.poly, e.W, e.H);
    const tb = M.pupilTimmBarth(e.g, e.W, e.H, m), dc = M.pupilDarkCentroid(e.g, e.W, e.H, m);
    assert.ok(Math.hypot(tb[0] - ix, tb[1] - iy) < 1.5, `TB ${tb} vs ${ix},${iy}`);
    assert.ok(Math.hypot(dc[0] - ix, dc[1] - iy) < 2.5, `DC ${dc} vs ${ix},${iy}`);
  }
});

test('cropEyeFeatures: pupil moves with the iris, lids report the aperture, patch is equalised', () => {
  const f1 = M.cropEyeFeatures(...Object.values(synthEye(40, 27)).slice(0, 3), synthEye(40, 27).poly, { patch: [15, 9] });
  const f2 = M.cropEyeFeatures(...Object.values(synthEye(52, 27)).slice(0, 3), synthEye(52, 27).poly, { patch: [15, 9] });
  assert.ok(f2.tb[0] - f1.tb[0] > 0.15 && f2.tb[0] - f1.tb[0] < 0.25, 'normalised x shift = 12 px / 60 px eye width');
  const wide = synthEye(45, 27, { open: 14 }), narrow = synthEye(45, 27, { open: 8 });
  const fw = M.cropEyeFeatures(wide.g, 90, 54, wide.poly), fn = M.cropEyeFeatures(narrow.g, 90, 54, narrow.poly);
  assert.ok(fw.upper < fn.upper && fw.lower > fn.lower, 'upper lid higher / lower lid lower when the eye is wider open');
  assert.strictEqual(f1.patch.length, 135);
  const mean = f1.patch.reduce((a, b) => a + b, 0) / 135; assert.ok(Math.abs(mean - 0.5) < 0.05, 'rank-equalised patch has mean ~0.5');
});

test('cropVec yields 8 values with NaN for missing parts and falls back to the dark centroid', () => {
  const v = M.cropVec({ r: { tb: null, dc: [0.1, 0.02], upper: -0.2, lower: 0.2 }, l: null });
  assert.strictEqual(v.length, M.CROP_NAMES.length);
  assert.deepStrictEqual(v.slice(0, 2), [0.1, 0.02]);
  assert.ok(Number.isNaN(v[2]) && Number.isNaN(v[3]) && Number.isNaN(v[6]));
  assert.ok(M.cropVec(null).every(Number.isNaN));
});

function synthRows(withCrop, noise, seed) {   // 9 dots x 30 frames; the geometric estimate has no vertical information
  let s = seed || 3; const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647 - 0.5; };
  const rows = [];
  for (const ty of [100, 450, 800]) for (const tx of [100, 720, 1340]) for (let k = 0; k < 30; k++) {
    const vec = new Array(23).fill(0).map(() => rnd() * 0.01);
    vec[0] = tx + rnd() * 60; vec[1] = 450 + rnd() * 300;
    vec[2] = (tx - 720) / 4000 + rnd() * 0.02; vec[3] = (ty - 450) / 8000 + rnd() * noise;   // MediaPipe iris: weak, noisy vertical
    const crop = withCrop ? [(tx - 720) / 3000 + rnd() * 0.01, (ty - 450) / 5000 + rnd() * 0.01, (tx - 720) / 3000 + rnd() * 0.01, (ty - 450) / 5000 + rnd() * 0.01,
      -0.2 - (ty - 450) / 9000 + rnd() * 0.01, 0.2 + rnd() * 0.01, -0.2 - (ty - 450) / 9000 + rnd() * 0.01, 0.2 + rnd() * 0.01] : [];
    rows.push({ vec: vec.concat(crop), x: tx, y: ty });
  }
  return rows;
}

test('GazeRegressor uses crop features (grouped-CV lambda) when present and they help', () => {
  const base = new M.GazeRegressor(), crop = new M.GazeRegressor();
  synthRows(false, 0.3).forEach((r) => base.addCalibration(r.vec, r.x, r.y));
  synthRows(true, 0.3).forEach((r) => crop.addCalibration(r.vec, r.x, r.y));
  base.fit(); crop.fit();
  assert.strictEqual(base.model.crop, false); assert.strictEqual(base.model.lambdaSel, 'gcv');
  assert.strictEqual(crop.model.crop, true); assert.strictEqual(crop.model.lambdaSel, 'cv');
  const held = synthRows(true, 0.3, 99);
  const errY = (reg, strip) => held.reduce((a, r) => a + Math.abs(reg.predict(strip ? r.vec.slice(0, 23) : r.vec).y - r.y), 0) / held.length;
  assert.ok(errY(crop) < errY(base, true) * 0.5, `vertical error crop ${errY(crop)} vs base ${errY(base, true)}`);
});

test('missing crop features (NaN or stage switched off) are treated as the mean, not as zeros', () => {
  const reg = new M.GazeRegressor();
  const rows = synthRows(true, 0.3);
  rows.forEach((r, i) => { const v = r.vec.slice(); if (i % 7 === 0) for (let k = 23; k < 31; k++) v[k] = NaN; reg.addCalibration(v, r.x, r.y); });
  reg.fit();
  assert.ok(reg.model && reg.model.crop);
  const p = reg.predict(rows[0].vec.slice(0, 23));      // 23-dim vec after the crop stage turned itself off
  assert.ok(Number.isFinite(p.x) && Number.isFinite(p.y));
  const q = reg.predict(rows[0].vec.slice(0, 23).concat(new Array(8).fill(NaN)));
  assert.ok(Math.abs(p.x - q.x) < 1e-9 && Math.abs(p.y - q.y) < 1e-9);
});

test('cvGroups bins targets on a 3x3 grid (9-dot calibration = leave-one-dot-out)', () => {
  const rows = []; for (const y of [50, 450, 850]) for (const x of [50, 720, 1390]) rows.push({ x, y }, { x: x + 3, y });
  const g = M.cvGroups(rows);
  assert.strictEqual(new Set(g).size, 9); assert.strictEqual(g[0], g[1]);
  const cv = M.cvLambda(synthRows(true, 0.3).map((r) => ({ f: r.vec, x: r.x - r.vec[0], y: r.y - r.vec[1], w: 1 })), M.EYE_IDX.concat(M.CROP_IDX), [0.1, 10, 1000]);
  assert.ok(cv && [0.1, 10, 1000].includes(cv.lambda) && cv.cvErr > 0);
});
