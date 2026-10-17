/* Helix gaze model: pure functions (browser + node), no DOM.
   MediaPipe Face Landmarker (478 landmarks incl. iris) + facial transformation matrix
   -> eye-region features (iris offset inside each eye, lid position, openness), head pose
   (yaw/pitch/roll + position) -> per-user weighted ridge regression to screen px, with the
   ridge strength picked by generalised cross-validation and continuous online adaptation
   from implicit samples (clicks, taps, caret). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.HelixModel = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // MediaPipe face mesh indices (subject's right eye = image-left when not mirrored)
  var LM = {
    R_OUT: 33, R_IN: 133, R_UP: 159, R_LO: 145, R_IRIS: 468, R_IRIS_A: 469, R_IRIS_B: 471,
    L_IN: 362, L_OUT: 263, L_UP: 386, L_LO: 374, L_IRIS: 473, L_IRIS_A: 474, L_IRIS_B: 476,
    CHEEK_R: 234, CHEEK_L: 454, TOP: 10, CHIN: 152, NOSE: 1
  };
  var IRIS_DIAMETER_CM = 1.17;  // human iris diameter is remarkably constant (~11.7 mm)
  // vec layout: [geometric screen estimate (2) | eye-in-head features (11) | head pose + position (6)]
  var FEATURE_NAMES = ['gx', 'gy', 'uR', 'vR', 'uL', 'vL', 'lidR', 'lidL', 'openR', 'openL', 'u2', 'v2', 'uv',
    'yaw', 'pitch', 'roll', 'faceX', 'faceY', 'faceW', 'lookHR', 'lookVR', 'lookHL', 'lookVL'];
  // last four: MediaPipe blendshape eye-look scores (0 when unavailable, e.g. synthetic streams)
  var GEO_IDX = [0, 1], EYE_IDX = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 19, 20, 21, 22], ALL_IDX = FEATURE_NAMES.map(function (_, i) { return i; });
  var EYE_GAIN = 2.3;   // sin(eye rotation) ~= iris offset / eye width * (eye width / eyeball radius ~ 2.8/1.2)

  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1]; }
  function len(a) { return Math.hypot(a[0], a[1]); }
  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }

  /* Head pose from MediaPipe's 4x4 column-major facial transformation matrix. Angles in radians. */
  function headPose(m) {
    if (!m || m.length < 16) return null;
    var R = function (r, c) { return m[c * 4 + r]; };
    var sy = Math.hypot(R(2, 1), R(2, 2));
    return {
      pitch: Math.atan2(R(2, 1), R(2, 2)),
      yaw: Math.atan2(-R(2, 0), sy),
      roll: Math.atan2(R(1, 0), R(0, 0)),
      tx: m[12], ty: m[13], tz: m[14]
    };
  }

  function eye(P, a, b, up, lo, iris) {
    var A = P(a), B = P(b);
    if (A[0] > B[0]) { var t = A; A = B; B = t; }   // axis always points image-right
    var axis = sub(B, A), ew = len(axis) || 1;
    var e = [axis[0] / ew, axis[1] / ew], n = [-e[1], e[0]];   // n points image-down
    var c = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2], I = P(iris);
    var U = P(up), L = P(lo), lid = [(U[0] + L[0]) / 2, (U[1] + L[1]) / 2];
    return {
      u: dot(sub(I, c), e) / ew, v: dot(sub(I, c), n) / ew,
      lid: dot(sub(I, lid), n) / ew, open: dot(sub(L, U), n) / ew, width: ew
    };
  }

  /* landmarks: array of {x,y,z} normalised to the video frame; W,H: frame size in px;
     matrix: optional facialTransformationMatrix.data. Returns null if landmarks are incomplete. */
  function eyeFeatures(lm, W, H, matrix, opts) {
    if (!lm || lm.length < 478) return null;
    opts = opts || {};
    var P = function (i) { var p = lm[i]; return [p.x * W, p.y * H]; };
    var r = eye(P, LM.R_OUT, LM.R_IN, LM.R_UP, LM.R_LO, LM.R_IRIS);
    var l = eye(P, LM.L_IN, LM.L_OUT, LM.L_UP, LM.L_LO, LM.L_IRIS);
    var cr = P(LM.CHEEK_R), cl = P(LM.CHEEK_L), top = P(LM.TOP), chin = P(LM.CHIN), nose = P(LM.NOSE);
    var faceWpx = len(sub(cl, cr));
    var pose = headPose(matrix);
    if (!pose) {  // geometric fallback when no matrix is available
      var mid = [(cr[0] + cl[0]) / 2, (cr[1] + cl[1]) / 2];
      pose = {
        yaw: Math.asin(clamp((nose[0] - mid[0]) / (faceWpx / 2 || 1), -1, 1)),
        pitch: Math.asin(clamp((nose[1] - (top[1] + chin[1]) / 2) / ((chin[1] - top[1]) / 2 || 1), -1, 1)),
        roll: Math.atan2(cl[1] - cr[1], cl[0] - cr[0]), tx: 0, ty: 0, tz: 0
      };
    }
    var irisPx = (len(sub(P(LM.R_IRIS_A), P(LM.R_IRIS_B))) + len(sub(P(LM.L_IRIS_A), P(LM.L_IRIS_B)))) / 2;
    var hfov = (opts.hfovDeg || 60) * Math.PI / 180;      // typical webcam/phone front camera
    var focal = W / (2 * Math.tan(hfov / 2));
    var distanceCm = irisPx > 0.5 ? focal * IRIS_DIAMETER_CM / irisPx : null;
    var u = (r.u + l.u) / 2, v = (r.v + l.v) / 2;
    // Geometric gaze point (cm, image-aligned axes) = eye position + D * tan(head angle + eye angle).
    // Head angles come from the landmarks themselves (nose vs. cheeks / brow-chin), so their sign
    // convention matches the iris offsets by construction; the regression then only has to learn an
    // affine map from this to screen px, which keeps working when the head moves after calibration.
    var mid = [(cr[0] + cl[0]) / 2, (cr[1] + cl[1]) / 2];
    var hYaw = Math.asin(clamp((nose[0] - mid[0]) / (faceWpx / 2 || 1), -0.9, 0.9));
    var faceHpx = len(sub(chin, top)) || 1;
    var hPitch = Math.asin(clamp((nose[1] - (top[1] + chin[1]) / 2) / (faceHpx / 2), -0.9, 0.9));
    var D = distanceCm || 55;
    var ex = Math.asin(clamp(EYE_GAIN * u, -0.95, 0.95)), ey = Math.asin(clamp(EYE_GAIN * v, -0.95, 0.95));
    var eyeX = ((r.width ? (P(LM.R_IRIS)[0] + P(LM.L_IRIS)[0]) / 2 : mid[0]) - W / 2) / focal;
    var eyeY = ((P(LM.R_IRIS)[1] + P(LM.L_IRIS)[1]) / 2 - H / 2) / focal;
    var gx = D * (eyeX + Math.tan(hYaw + ex)), gy = D * (eyeY + Math.tan(hPitch + ey));
    var bs = blendMap(opts.blendshapes);
    var vec = [gx, gy, r.u, r.v, l.u, l.v, r.lid, l.lid, r.open, l.open, u * u, v * v, u * v,
      pose.yaw, pose.pitch, pose.roll, mid[0] / W, (top[1] + chin[1]) / 2 / H, faceWpx / W,
      (bs.eyeLookOutRight || 0) - (bs.eyeLookInRight || 0), (bs.eyeLookUpRight || 0) - (bs.eyeLookDownRight || 0),
      (bs.eyeLookInLeft || 0) - (bs.eyeLookOutLeft || 0), (bs.eyeLookUpLeft || 0) - (bs.eyeLookDownLeft || 0)];
    var open = (r.open + l.open) / 2;
    // Lids drop a lot when someone looks DOWN (e.g. at the bottom of the page), so narrow eyes
    // are only a blink when the narrowing is not explained by downward gaze. Measured on the
    // recorded clip: 30% of frames had open<0.13 while eyeLookDown was ~0.8 (runs up to 2.5 s,
    // i.e. reading downward, not blinking); a fixed threshold threw all of those away.
    var hasBs = opts.blendshapes && opts.blendshapes.length;
    var lookDown = ((bs.eyeLookDownLeft || 0) + (bs.eyeLookDownRight || 0)) / 2;
    var blink = hasBs
      ? open < 0.04 || (lookDown < 0.35 && (open < 0.12 || (bs.eyeBlinkLeft > 0.7 && bs.eyeBlinkRight > 0.7)))
      : open < 0.07;
    return {
      vec: vec, pose: pose, distanceCm: distanceCm, open: open, blink: blink, lookDown: lookDown,
      blinkScore: hasBs ? ((bs.eyeBlinkLeft || 0) + (bs.eyeBlinkRight || 0)) / 2 : null,
      face: { x: (cr[0] + cl[0]) / 2 / W, y: (top[1] + chin[1]) / 2 / H, w: faceWpx / W, h: (chin[1] - top[1]) / H },
      eyes: { r: r, l: l }
    };
  }

  function blendMap(cats) {
    var m = {};
    (cats || []).forEach(function (c) { if (c && c.categoryName) m[c.categoryName] = c.score; });
    return m;
  }

  /* ---------- linear algebra (small symmetric systems) ---------- */
  function jacobiEigen(A) {          // A: symmetric p x p (array of arrays). Returns {d, V} (columns = vectors)
    var p = A.length, a = A.map(function (r) { return r.slice(); }), V = [], i, j, k;
    for (i = 0; i < p; i++) { V.push(new Array(p).fill(0)); V[i][i] = 1; }
    for (var sweep = 0; sweep < 60; sweep++) {
      var off = 0;
      for (i = 0; i < p; i++) for (j = i + 1; j < p; j++) off += a[i][j] * a[i][j];
      if (off < 1e-18) break;
      for (i = 0; i < p; i++) for (j = i + 1; j < p; j++) {
        if (Math.abs(a[i][j]) < 1e-30) continue;
        var th = (a[j][j] - a[i][i]) / (2 * a[i][j]);
        var t = (th >= 0 ? 1 : -1) / (Math.abs(th) + Math.sqrt(th * th + 1));
        var c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (k = 0; k < p; k++) { var aki = a[k][i], akj = a[k][j]; a[k][i] = c * aki - s * akj; a[k][j] = s * aki + c * akj; }
        for (k = 0; k < p; k++) { var aik = a[i][k], ajk = a[j][k]; a[i][k] = c * aik - s * ajk; a[j][k] = s * aik + c * ajk; }
        for (k = 0; k < p; k++) { var vki = V[k][i], vkj = V[k][j]; V[k][i] = c * vki - s * vkj; V[k][j] = s * vki + c * vkj; }
      }
    }
    return { d: a.map(function (r, idx) { return r[idx]; }), V: V };
  }

  var LAMBDAS = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100];

  /* Weighted ridge regression x,y = f(features), standardised features, intercept unpenalised,
     lambda chosen by GCV. Calibration samples are kept; implicit samples live in a ring buffer
     with age decay, so the model keeps adapting while the student reads. */
  function GazeRegressor(opts) {
    opts = opts || {};
    this.maxCal = opts.maxCal || 600;
    this.maxImplicit = opts.maxImplicit || 150;
    this.implicitWeight = opts.implicitWeight == null ? 0.6 : opts.implicitWeight;
    this.halfLifeMs = opts.halfLifeMs || 10 * 60 * 1000;
    this.cal = []; this.implicit = [];
    this.model = null;
    this.features = opts.features || null;  // optional index subset (ablation studies)
    // 'hybrid' (default): affine map of the geometric estimate + ridge on eye features for the residual.
    // 'ridge': one ridge model over the chosen features (used for ablations).
    this.mode = opts.mode || (opts.features ? 'ridge' : 'hybrid');
  }
  GazeRegressor.prototype._f = function (vec) {
    if (!this.features) return vec;
    return this.features.map(function (i) { return vec[i]; });
  };
  GazeRegressor.prototype.addCalibration = function (vec, x, y, w) {
    this.cal.push({ f: this._f(vec), x: x, y: y, w: w == null ? 1 : w, t: Date.now() });
    if (this.cal.length > this.maxCal) this.cal.splice(0, this.cal.length - this.maxCal);
  };
  GazeRegressor.prototype.addImplicit = function (vec, x, y, w, t) {
    this.implicit.push({ f: this._f(vec), x: x, y: y, w: (w == null ? 1 : w) * this.implicitWeight, t: t || Date.now() });
    if (this.implicit.length > this.maxImplicit) this.implicit.shift();
  };
  GazeRegressor.prototype.clear = function () { this.cal = []; this.implicit = []; this.model = null; };
  GazeRegressor.prototype.size = function () { return this.cal.length + this.implicit.length; };
  GazeRegressor.prototype._rows = function (nowT) {
    var self = this, t0 = nowT || Date.now();
    return this.cal.concat(this.implicit.map(function (s) {
      var age = Math.max(0, t0 - s.t);
      return { f: s.f, x: s.x, y: s.y, w: s.w * Math.pow(0.5, age / self.halfLifeMs) };
    }));
  };
  GazeRegressor.prototype.fit = function (nowT) {
    var rows = this._rows(nowT);
    if (rows.length < 8) return (this.model = null);
    if (this.mode === 'ridge') { this.model = ridgeFit(rows, null, LAMBDAS); if (this.model) this.model.kind = 'ridge'; return this.model; }
    // stage 1: weighted affine map (light ridge) of the geometric estimate
    var geo = ridgeFit(rows, GEO_IDX, [1e-3]);
    if (!geo) return (this.model = null);
    // stage 2: residual correction from eye-in-head features only (no head-position terms)
    var resid = rows.map(function (r) { var g = ridgePredict(geo, r.f); return { f: r.f, x: r.x - g.x, y: r.y - g.y, w: r.w }; });
    var eye = ridgeFit(resid, EYE_IDX, LAMBDAS);
    var rss = 0, W = 0;
    rows.forEach(function (r) { var p = ridgePredict(geo, r.f), q = ridgePredict(eye, r.f); W += r.w; rss += r.w * (Math.pow(p.x + q.x - r.x, 2) + Math.pow(p.y + q.y - r.y, 2)); });
    this.model = { kind: 'hybrid', geo: geo, eye: eye, lambda: eye ? eye.lambda : null, n: rows.length, rmsPx: Math.sqrt(rss / W), bias: { x: 0, y: 0 } };
    this.model.bias = this._implicitBias(nowT);
    return this.model;
  };
  /* stage 3 (online adaptation): recent implicit samples (clicks/taps/caret) estimate the current
     offset caused by head movement or drift; shrunk toward zero so a couple of odd clicks can't
     drag the estimate around. */
  GazeRegressor.prototype._implicitBias = function (nowT) {
    if (!this.model || !this.implicit.length) return { x: 0, y: 0 };
    var t0 = nowT || Date.now(), sx = 0, sy = 0, sw = 0, self = this, k = 0;
    var recent = this.implicit.slice(-30);
    recent.forEach(function (s) {
      var age = Math.max(0, t0 - s.t), w = Math.pow(0.5, age / (self.halfLifeMs / 4)) * (0.6 + 0.4 * (++k / recent.length));
      var p = self._predictRaw(s.f);
      sx += w * (s.x - p.x); sy += w * (s.y - p.y); sw += w;
    });
    var shrink = sw / (sw + 3);
    return { x: shrink * sx / (sw || 1), y: shrink * sy / (sw || 1) };
  };
  GazeRegressor.prototype._predictRaw = function (f) {
    var m = this.model;
    if (m.kind === 'ridge') return ridgePredict(m, f);
    var p = ridgePredict(m.geo, f), q = m.eye ? ridgePredict(m.eye, f) : { x: 0, y: 0 };
    return { x: p.x + q.x, y: p.y + q.y };
  };
  GazeRegressor.prototype.predict = function (vec) {
    var m = this.model;
    if (!m) return null;
    var p = this._predictRaw(this._f(vec)), b = m.bias || { x: 0, y: 0 };
    return { x: p.x + b.x, y: p.y + b.y };
  };

  function ridgePredict(m, f) {
    var x = m.mx, y = m.my, idx = m.idx;
    for (var a = 0; a < idx.length; a++) { var z = (f[idx[a]] - m.mu[a]) / m.sd[a]; x += z * m.wx[a]; y += z * m.wy[a]; }
    return { x: x, y: y };
  }

  /* Weighted ridge over columns idx (null = all), standardised, intercept unpenalised,
     lambda chosen from `lambdas` by generalised cross-validation (closed form via eigendecomposition). */
  function ridgeFit(rowsIn, idx, lambdas) {
    var rows = rowsIn;
    var n = rows.length;
    if (!n) return null;
    idx = idx || rows[0].f.map(function (_, q) { return q; });
    rows = rows.map(function (r) { return { f: idx.map(function (q) { return r.f[q]; }), x: r.x, y: r.y, w: r.w }; });
    var p = idx.length, i, j, k;
    var W = 0, mu = new Array(p).fill(0), mx = 0, my = 0;
    rows.forEach(function (r) { W += r.w; mx += r.w * r.x; my += r.w * r.y; for (var q = 0; q < p; q++) mu[q] += r.w * r.f[q]; });
    mx /= W; my /= W; for (j = 0; j < p; j++) mu[j] /= W;
    var sd = new Array(p).fill(0);
    rows.forEach(function (r) { for (var q = 0; q < p; q++) sd[q] += r.w * Math.pow(r.f[q] - mu[q], 2); });
    for (j = 0; j < p; j++) sd[j] = Math.sqrt(sd[j] / W) || 1;
    // Z = sqrt(w) * standardised features
    var Z = rows.map(function (r) { var s = Math.sqrt(r.w); return r.f.map(function (v, q) { return s * (v - mu[q]) / sd[q]; }); });
    var tx = rows.map(function (r) { return Math.sqrt(r.w) * (r.x - mx); });
    var ty = rows.map(function (r) { return Math.sqrt(r.w) * (r.y - my); });
    var G = []; for (i = 0; i < p; i++) G.push(new Array(p).fill(0));
    var bx = new Array(p).fill(0), by = new Array(p).fill(0);
    for (k = 0; k < n; k++) {
      var z = Z[k];
      for (i = 0; i < p; i++) {
        bx[i] += z[i] * tx[k]; by[i] += z[i] * ty[k];
        for (j = i; j < p; j++) G[i][j] += z[i] * z[j];
      }
    }
    for (i = 0; i < p; i++) for (j = 0; j < i; j++) G[i][j] = G[j][i];
    var E = jacobiEigen(G), V = E.V, d = E.d;
    var px = new Array(p).fill(0), py = new Array(p).fill(0);   // V^T b
    for (j = 0; j < p; j++) for (i = 0; i < p; i++) { px[j] += V[i][j] * bx[i]; py[j] += V[i][j] * by[i]; }
    var best = null;
    lambdas.forEach(function (lam) {
      var wx = new Array(p).fill(0), wy = new Array(p).fill(0), df = 0;
      for (j = 0; j < p; j++) {
        var g = 1 / (Math.max(d[j], 0) + lam);
        df += Math.max(d[j], 0) * g;
        for (i = 0; i < p; i++) { wx[i] += V[i][j] * g * px[j]; wy[i] += V[i][j] * g * py[j]; }
      }
      var rss = 0;
      for (k = 0; k < n; k++) {
        var ex = tx[k], ey = ty[k];
        for (i = 0; i < p; i++) { ex -= Z[k][i] * wx[i]; ey -= Z[k][i] * wy[i]; }
        rss += ex * ex + ey * ey;
      }
      var gcv = n * rss / Math.pow(Math.max(1, n - df), 2);
      if (!best || gcv < best.gcv) best = { gcv: gcv, lam: lam, wx: wx, wy: wy, df: df, rss: rss };
    });
    return { idx: idx, mu: mu, sd: sd, mx: mx, my: my, wx: best.wx, wy: best.wy, lambda: best.lam, df: best.df,
             n: n, rmsPx: Math.sqrt(best.rss / W) };
  }

  /* Keep one regressor per screen orientation (phones/tablets): rotating the device changes the
     camera-to-screen geometry completely, so a portrait model is useless in landscape. */
  function OrientationModels(opts) { this.opts = opts || {}; this.models = {}; this.key = null; }
  OrientationModels.prototype.use = function (key) {
    this.key = key;
    if (!this.models[key]) this.models[key] = new GazeRegressor(this.opts);
    return this.models[key];
  };
  OrientationModels.prototype.current = function () { return this.key ? this.use(this.key) : null; };
  OrientationModels.prototype.ready = function (key) { var m = this.models[key || this.key]; return !!(m && m.model); };

  /* ---------- positioning guidance before calibration ---------- */
  function poseGuidance(feat, opts) {
    opts = opts || {};
    var mobile = !!opts.mobile;
    var checks = [];
    if (!feat) return { ok: false, checks: [{ key: 'face', ok: false, label: 'Face not found', hint: 'Look at the screen with your whole face in the camera view.' }] };
    var deg = function (r) { return r * 180 / Math.PI; };
    var dist = feat.distanceCm, lo = mobile ? 20 : 33, hi = mobile ? 55 : 85;
    checks.push(dist == null ? { key: 'distance', ok: true, label: 'Distance unknown' } :
      dist < lo ? { key: 'distance', ok: false, label: 'Too close (~' + Math.round(dist) + ' cm)', hint: 'Move back a little.' } :
      dist > hi ? { key: 'distance', ok: false, label: 'Too far (~' + Math.round(dist) + ' cm)', hint: mobile ? 'Hold the phone a bit closer.' : 'Move a little closer to the screen.' } :
      { key: 'distance', ok: true, label: 'Distance ~' + Math.round(dist) + ' cm' });
    var cx = feat.face.x, cy = feat.face.y;
    var centred = Math.abs(cx - 0.5) < 0.2 && Math.abs(cy - 0.5) < 0.25;
    checks.push({ key: 'centre', ok: centred, label: centred ? 'Face centred' : 'Off centre',
      hint: Math.abs(cx - 0.5) >= 0.2 ? 'Move so your face is in the middle of the preview.' : (cy < 0.5 ? (mobile ? 'Tilt the phone up slightly.' : 'Lower the camera or sit up.') : (mobile ? 'Tilt the phone down slightly.' : 'Raise the screen or sit lower.')) });
    var yaw = deg(feat.pose.yaw), pitch = deg(feat.pose.pitch), roll = deg(feat.pose.roll);
    var facing = Math.abs(yaw) < 15 && Math.abs(pitch) < 18;
    checks.push({ key: 'facing', ok: facing, label: facing ? 'Facing the screen' : 'Turn to face the screen',
      hint: Math.abs(yaw) >= 15 ? 'Turn your head toward the screen.' : 'Level your chin.' });
    var level = Math.abs(roll) < 10;
    checks.push({ key: 'level', ok: level, label: level ? 'Head level' : 'Head tilted', hint: 'Straighten your head.' });
    checks.push({ key: 'eyes', ok: !feat.blink, label: feat.blink ? 'Eyes not visible' : 'Eyes visible', hint: 'Open your eyes, remove glare (tilt glasses).' });
    if (opts.brightness != null) {
      var lit = opts.brightness > 55;
      checks.push({ key: 'light', ok: lit, label: lit ? 'Lighting OK' : 'Too dark', hint: 'Face a window or lamp; avoid a bright light behind you.' });
    }
    return { ok: checks.every(function (c) { return c.ok; }), checks: checks, yawDeg: yaw, pitchDeg: pitch, rollDeg: roll, distanceCm: dist };
  }

  /* ---------- honest error reporting ---------- */
  var CM_PER_CSS_PX = 2.54 / 96;  // CSS reference pixel; real devices differ, so degrees are an estimate
  function angularError(errPx, distanceCm, cmPerPx) {
    if (errPx == null || !distanceCm) return null;
    return Math.atan((errPx * (cmPerPx || CM_PER_CSS_PX)) / distanceCm) * 180 / Math.PI;
  }

  /* AOI resolution the measured accuracy can honestly support. Error is the validation
     median error in CSS px; metrics are typical paragraph/line heights on this page. */
  function aoiResolution(errPx, metrics) {
    metrics = metrics || {};
    var line = metrics.lineHeight || 26, para = metrics.paragraphHeight || 110;
    if (errPx == null || !isFinite(errPx)) return 'heading';
    if (errPx <= 0.75 * line) return 'line';
    if (errPx <= 0.6 * para) return 'paragraph';
    return 'heading';
  }

  /* Rolling accuracy estimate from implicit samples (where a click/tap/caret landed vs. where the
     model thought the eyes were). Used for the drift chart and adaptive recalibration. */
  function DriftTracker(opts) {
    opts = opts || {};
    this.window = opts.window || 9; this.errs = []; this.points = []; this.maxPoints = opts.maxPoints || 240;
  }
  DriftTracker.prototype.add = function (errPx, t, source) {
    this.errs.push(errPx); if (this.errs.length > this.window) this.errs.shift();
    var m = this.median();
    this.points.push({ t: t, err: Math.round(errPx), med: Math.round(m), src: source || 'click' });
    if (this.points.length > this.maxPoints) this.points.shift();
    return m;
  };
  // after a recalibration: start a fresh median window but keep the chart history (with a marker)
  DriftTracker.prototype.reset = function (t) {
    this.errs = [];
    if (this.points.length) this.points.push({ t: t, err: null, med: null, src: 'recal' });
  };
  DriftTracker.prototype.median = function () {
    if (!this.errs.length) return null;
    var s = this.errs.slice().sort(function (a, b) { return a - b; }), h = s.length >> 1;
    return s.length % 2 ? s[h] : (s[h - 1] + s[h]) / 2;
  };
  DriftTracker.prototype.drifting = function (baselinePx, factor) {
    var m = this.median();
    return this.errs.length >= Math.min(5, this.window) && m != null && m > Math.max(120, (baselinePx || 0) * (factor || 1.8));
  };

  return { LM: LM, FEATURE_NAMES: FEATURE_NAMES, GEO_IDX: GEO_IDX, EYE_IDX: EYE_IDX, ridgeFit: ridgeFit, headPose: headPose, eyeFeatures: eyeFeatures,
    jacobiEigen: jacobiEigen, GazeRegressor: GazeRegressor, OrientationModels: OrientationModels,
    poseGuidance: poseGuidance, angularError: angularError, aoiResolution: aoiResolution,
    DriftTracker: DriftTracker, CM_PER_CSS_PX: CM_PER_CSS_PX, IRIS_DIAMETER_CM: IRIS_DIAMETER_CM };
});
