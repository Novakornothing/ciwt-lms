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
  /* Pass 5: optional second-stage eye-crop features appended to vec when the high-res crop stage runs
     (desktop): pupil centre in the pose-normalised crop (Timm & Barth, dark-centroid fallback) and the
     upper/lower lid position, both in units of eye width. Missing values are NaN = "no information". */
  var CROP_NAMES = ['pupilXR', 'pupilYR', 'pupilXL', 'pupilYL', 'lidUpR', 'lidLoR', 'lidUpL', 'lidLoL'];
  var CROP_IDX = CROP_NAMES.map(function (_, i) { return 23 + i; });
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

  function irisCentroid(lm, P, cIdx, ringIdx) {
    var c = P(cIdx), sx = c[0], sy = c[1], n = 1;
    for (var k = 0; k < ringIdx.length; k++) {
      var p = lm[ringIdx[k]];
      if (p && typeof p.x === 'number' && isFinite(p.x) && isFinite(p.y)) {
        sx += p.x * (c[0] / (lm[cIdx].x || 1));
      }
    }
    // Use P() directly when ring landmarks are valid
    sx = c[0]; sy = c[1]; n = 1;
    for (var j = 0; j < ringIdx.length; j++) {
      var rk = ringIdx[j];
      if (lm[rk] && typeof lm[rk].x === 'number' && isFinite(lm[rk].x) && isFinite(lm[rk].y)) {
        var q = P(rk);
        sx += q[0]; sy += q[1]; n++;
      }
    }
    return [sx / n, sy / n];
  }

  function eye(P, a, b, up, lo, iris, lm, ring) {
    var A = P(a), B = P(b);
    if (A[0] > B[0]) { var t = A; A = B; B = t; }   // axis always points image-right
    var axis = sub(B, A), ew = len(axis) || 1;
    var e = [axis[0] / ew, axis[1] / ew], n = [-e[1], e[0]];   // n points image-down
    var c = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2];
    var I = (lm && ring) ? irisCentroid(lm, P, iris, ring) : P(iris);
    var U = P(up), L = P(lo), lid = [(U[0] + L[0]) / 2, (U[1] + L[1]) / 2];
    return {
      u: dot(sub(I, c), e) / ew, v: dot(sub(I, c), n) / ew,
      lid: dot(sub(I, lid), n) / ew, open: dot(sub(L, U), n) / ew, width: ew, center: I
    };
  }

  /* landmarks: array of {x,y,z} normalised to the video frame; W,H: frame size in px;
     matrix: optional facialTransformationMatrix.data. Returns null if landmarks are incomplete. */
  function eyeFeatures(lm, W, H, matrix, opts) {
    if (!lm || lm.length < 478) return null;
    opts = opts || {};
    var P = function (i) { var p = lm[i]; return [p.x * W, p.y * H]; };
    var r = eye(P, LM.R_OUT, LM.R_IN, LM.R_UP, LM.R_LO, LM.R_IRIS, lm, [469, 470, 471, 472]);
    var l = eye(P, LM.L_IN, LM.L_OUT, LM.L_UP, LM.L_LO, LM.L_IRIS, lm, [474, 475, 476, 477]);
    var cr = P(LM.CHEEK_R), cl = P(LM.CHEEK_L), top = P(LM.TOP), chin = P(LM.CHIN), nose = P(LM.NOSE);
    var faceWpx = len(sub(cl, cr));
    var hasMat = !!(matrix && matrix.length >= 16);
    var pose = headPose(matrix);
    if (!pose) {  // geometric fallback when no matrix is available
      var mid0 = [(cr[0] + cl[0]) / 2, (cr[1] + cl[1]) / 2];
      pose = {
        yaw: Math.asin(clamp((nose[0] - mid0[0]) / (faceWpx / 2 || 1), -1, 1)),
        pitch: Math.asin(clamp((nose[1] - (top[1] + chin[1]) / 2) / ((chin[1] - top[1]) / 2 || 1), -1, 1)),
        roll: Math.atan2(cl[1] - cr[1], cl[0] - cr[0]), tx: 0, ty: 0, tz: 0
      };
    }
    var irisPx = (len(sub(P(LM.R_IRIS_A), P(LM.R_IRIS_B))) + len(sub(P(LM.L_IRIS_A), P(LM.L_IRIS_B)))) / 2;
    var hfov = (opts.hfovDeg || 60) * Math.PI / 180;      // typical webcam/phone front camera
    var focal = W / (2 * Math.tan(hfov / 2));
    var distanceCm = irisPx > 0.5 ? focal * IRIS_DIAMETER_CM / irisPx : null;
    var u = (r.u + l.u) / 2, v = (r.v + l.v) / 2;
    var mid = [(cr[0] + cl[0]) / 2, (cr[1] + cl[1]) / 2];
    var eyeX = ((r.width ? (r.center[0] + l.center[0]) / 2 : mid[0]) - W / 2) / focal;
    var eyeY = ((r.center[1] + l.center[1]) / 2 - H / 2) / focal;
    // Correct 2D nose-to-cheek ratio for perspective parallax when head translates sideways/vertically,
    // and fuse with 3D facialTransformationMatrix pose when available.
    var hYawRaw = Math.asin(clamp((nose[0] - mid[0]) / (faceWpx / 2 || 1), -0.9, 0.9));
    var faceHpx = len(sub(chin, top)) || 1;
    var hPitchRaw = Math.asin(clamp((nose[1] - (top[1] + chin[1]) / 2) / (faceHpx / 2), -0.9, 0.9));
    var hYaw = hasMat ? (0.82 * hYawRaw + 0.18 * (-pose.yaw)) : hYawRaw;
    var hPitch = hasMat ? (0.60 * hPitchRaw + 0.40 * (pose.pitch + 0.15)) : hPitchRaw;
    var D = distanceCm || 55;
    var ex = Math.asin(clamp(EYE_GAIN * u, -0.95, 0.95)), ey = Math.asin(clamp(EYE_GAIN * v, -0.95, 0.95));
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


  /* ---------- second stage: high-resolution eye crops (pass 5) ----------
     MediaPipe localises the iris inside a ~256 px face crop, so on a 720p/1080p camera most of the
     eye detail is thrown away. This stage samples each eye from the FULL camera frame into a
     pose-normalised crop (rotated/scaled by the eye-corner line), then
       - finds the eye centre with the gradient method of Timm & Barth (2011) restricted to the
         lid opening, and a dark-weighted centroid as a cheaper alternative;
       - builds a small histogram-equalised appearance patch (WebGazer-style, but pose-normalised).
     Everything here is pure (works on a grey Uint8/Float array) so node tests and the bench use
     exactly the browser code. */
  var CROP = { W: 90, H: 54, SPAN: 1.5 };   // crop covers 1.5 x eye width horizontally, 0.9 x vertically
  var R_CONTOUR = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7];
  var L_CONTOUR = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382];

  /* affine frame->crop map for one eye: a b c d e f as in canvas setTransform (x' = a x + c y + e) */
  function eyeCropTransform(A, B, opts) {
    opts = opts || {};
    var CW = opts.W || CROP.W, CH = opts.H || CROP.H, span = opts.span || CROP.SPAN;
    if (A[0] > B[0]) { var t = A; A = B; B = t; }
    var dx = B[0] - A[0], dy = B[1] - A[1], ew = Math.hypot(dx, dy) || 1;
    var cs = dx / ew, sn = dy / ew, S = CW / (span * ew);
    var cx = (A[0] + B[0]) / 2, cy = (A[1] + B[1]) / 2;
    var a = S * cs, b = -S * sn, c = S * sn, d = S * cs;
    return { a: a, b: b, c: c, d: d, e: CW / 2 - (a * cx + c * cy), f: CH / 2 - (b * cx + d * cy), W: CW, H: CH, scale: S, ew: ew,
             apply: function (p) { return [a * p[0] + c * p[1] + this.e, b * p[0] + d * p[1] + this.f]; } };
  }

  /* rows spans of a polygon (crop coords) -> mask Uint8Array(W*H) */
  function polygonMask(poly, W, H, grow) {
    var m = new Uint8Array(W * H), cx = 0, cy = 0;
    poly.forEach(function (p) { cx += p[0]; cy += p[1]; }); cx /= poly.length; cy /= poly.length;
    var P = poly.map(function (p) { return [cx + (p[0] - cx) * (grow || 1), cy + (p[1] - cy) * (grow || 1)]; });
    for (var y = 0; y < H; y++) {
      var xs = [], yy = y + 0.5;
      for (var i = 0, j = P.length - 1; i < P.length; j = i++) {
        var yi = P[i][1], yj = P[j][1];
        if ((yi > yy) !== (yj > yy)) xs.push(P[i][0] + (yy - yi) / (yj - yi) * (P[j][0] - P[i][0]));
      }
      xs.sort(function (p, q) { return p - q; });
      for (var k = 0; k + 1 < xs.length; k += 2) {
        for (var x = Math.max(0, Math.ceil(xs[k] - 0.5)); x <= Math.min(W - 1, Math.floor(xs[k + 1] - 0.5)); x++) m[y * W + x] = 1;
      }
    }
    return m;
  }

  function blur3(g, W, H) {   // separable [1 2 1]/4 smoothing
    var t = new Float32Array(W * H), o = new Float32Array(W * H), x, y, i;
    for (y = 0; y < H; y++) for (x = 0; x < W; x++) { i = y * W + x; t[i] = (g[y * W + Math.max(0, x - 1)] + 2 * g[i] + g[y * W + Math.min(W - 1, x + 1)]) / 4; }
    for (y = 0; y < H; y++) for (x = 0; x < W; x++) { i = y * W + x; o[i] = (t[Math.max(0, y - 1) * W + x] + 2 * t[i] + t[Math.min(H - 1, y + 1) * W + x]) / 4; }
    return o;
  }

  /* Timm & Barth (2011) eye-centre localisation: the centre is where the most normalised image
     gradients point radially away from (dark iris -> bright sclera), weighted by darkness.
     Candidates and gradients are restricted to the lid opening (mask). Returns crop px. */
  function pupilTimmBarth(gray, W, H, mask, opts) {
    opts = opts || {};
    var g = blur3(gray, W, H), gx = [], gy = [], px = [], py = [], mags = [], x, y, i;
    var gm = mask ? polygonDilate(mask, W, H, 2) : null;
    for (y = 1; y < H - 1; y++) for (x = 1; x < W - 1; x++) {
      i = y * W + x; if (gm && !gm[i]) continue;
      var ddx = (g[i + 1] - g[i - 1]) / 2, ddy = (g[i + W] - g[i - W]) / 2, mg = Math.hypot(ddx, ddy);
      mags.push(mg); gx.push(ddx); gy.push(ddy); px.push(x); py.push(y);
    }
    if (mags.length < 10) return null;
    var mu = 0, sd = 0; mags.forEach(function (v) { mu += v; }); mu /= mags.length;
    mags.forEach(function (v) { sd += (v - mu) * (v - mu); }); sd = Math.sqrt(sd / mags.length);
    var thr = mu + (opts.k == null ? 0.5 : opts.k) * sd, G = [];
    for (i = 0; i < mags.length; i++) if (mags[i] > thr) G.push([px[i], py[i], gx[i] / mags[i], gy[i] / mags[i]]);
    if (G.length < 6) return null;
    if (G.length > (opts.maxGrad || 400)) { var keep = Math.ceil(G.length / (opts.maxGrad || 400)); G = G.filter(function (_, q) { return q % keep === 0; }); }
    var maxI = 0; for (i = 0; i < g.length; i++) if (g[i] > maxI) maxI = g[i];
    // coarse grid (step 2 by default) then full-resolution refinement around the best candidate
    var step = opts.step || 2, best = -1, bx = 0, by = 0, obj = new Float32Array(W * H);
    var evalAt = function (x, y) {
      var i = y * W + x; if (obj[i] || (mask && !mask[i])) return;
      var sum = 0;
      for (var k = 0; k < G.length; k++) {
        var qx = G[k][0] - x, qy = G[k][1] - y, n = Math.hypot(qx, qy);
        if (n < 1) continue;
        var dp = (qx * G[k][2] + qy * G[k][3]) / n;
        if (dp > 0) sum += dp * dp;
      }
      var v = (maxI - g[i] + 1) * sum / G.length + 1e-9;
      obj[i] = v; if (v > best) { best = v; bx = x; by = y; }
    };
    for (y = 2; y < H - 2; y += step) for (x = 2; x < W - 2; x += step) evalAt(x, y);
    if (step > 1 && best > 0) {
      var cx0 = bx, cy0 = by, r = step + 1;
      for (y = Math.max(2, cy0 - r); y <= Math.min(H - 3, cy0 + r); y++) for (x = Math.max(2, cx0 - r); x <= Math.min(W - 3, cx0 + r); x++) evalAt(x, y);
    }
    if (best <= 0) return null;
    // sub-pixel: objective-weighted centroid of the 5x5 neighbourhood
    var sx = 0, sy = 0, sw = 0;
    for (y = Math.max(0, by - 2); y <= Math.min(H - 1, by + 2); y++) for (x = Math.max(0, bx - 2); x <= Math.min(W - 1, bx + 2); x++) {
      var w = obj[y * W + x] - 0.6 * best; if (w > 0) { sx += w * x; sy += w * y; sw += w; }
    }
    return sw ? [sx / sw, sy / sw] : [bx, by];
  }
  function polygonDilate(mask, W, H, r) {
    var o = new Uint8Array(W * H);
    for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
      if (!mask[y * W + x]) continue;
      for (var yy = Math.max(0, y - r); yy <= Math.min(H - 1, y + r); yy++) for (var xx = Math.max(0, x - r); xx <= Math.min(W - 1, x + r); xx++) o[yy * W + xx] = 1;
    }
    return o;
  }

  /* cheaper alternative: centroid of the darkest pixels inside the lid opening */
  function pupilDarkCentroid(gray, W, H, mask, frac) {
    var g = blur3(gray, W, H), vals = [];
    for (var i = 0; i < g.length; i++) if (!mask || mask[i]) vals.push(g[i]);
    if (vals.length < 10) return null;
    vals.sort(function (a, b) { return a - b; });
    var thr = vals[Math.floor(vals.length * (frac || 0.25))], sx = 0, sy = 0, sw = 0;
    for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
      var k = y * W + x; if (mask && !mask[k]) continue;
      var w = thr - g[k]; if (w > 0) { sx += w * x; sy += w * y; sw += w; }
    }
    return sw ? [sx / sw, sy / sw] : null;
  }

  /* appearance patch: area-average to pw x ph, then rank-equalise to [0,1] */
  function eyePatch(gray, W, H, pw, ph) {
    var out = new Float32Array(pw * ph), bw = W / pw, bh = H / ph;
    for (var j = 0; j < ph; j++) for (var i = 0; i < pw; i++) {
      var s = 0, n = 0;
      for (var y = Math.floor(j * bh); y < Math.floor((j + 1) * bh); y++) for (var x = Math.floor(i * bw); x < Math.floor((i + 1) * bw); x++) { s += gray[y * W + x]; n++; }
      out[j * pw + i] = n ? s / n : 0;
    }
    var idx = Array.prototype.map.call(out, function (v, k) { return k; }).sort(function (a, b) { return out[a] - out[b]; });
    var eq = new Float32Array(out.length);
    idx.forEach(function (k, r) { eq[k] = r / (idx.length - 1); });
    return eq;
  }

  /* all crop features for one eye. gray: crop pixels (W*H), polyCrop: lid contour in crop px */
  function cropEyeFeatures(gray, W, H, polyCrop, opts) {
    opts = opts || {};
    var mask = polygonMask(polyCrop, W, H, 1.0);
    var tb = opts.noTB ? null : pupilTimmBarth(gray, W, H, mask, { step: opts.tbStep || 2 });
    var dc = pupilDarkCentroid(gray, W, H, mask);
    var ewc = W / CROP.SPAN, cx = W / 2, cy = H / 2;
    var norm = function (p) { return p ? [(p[0] - cx) / ewc, (p[1] - cy) / ewc] : null; };
    // vertical cue from the lids themselves: upper/lower lid height at the centre column
    // (where the vertical line through the crop centre crosses the lid contour)
    var up = Infinity, lo = -Infinity, n = polyCrop.length;
    for (var i = 0, j = n - 1; i < n; j = i++) {
      var P = polyCrop[i], Q = polyCrop[j];
      if ((P[0] > cx) === (Q[0] > cx)) continue;
      var y = P[1] + (cx - P[0]) / (Q[0] - P[0]) * (Q[1] - P[1]);
      up = Math.min(up, y); lo = Math.max(lo, y);
    }
    if (!(lo > up)) { up = Infinity; lo = -Infinity; }
    return { tb: norm(tb), dc: norm(dc), upper: isFinite(up) ? (up - cy) / ewc : null, lower: isFinite(lo) ? (lo - cy) / ewc : null,
             patch: opts.patch ? eyePatch(gray, W, H, opts.patch[0], opts.patch[1]) : null };
  }

  /* crop features -> the 8 values appended to vec (CROP_NAMES); NaN where unavailable */
  function cropVec(crop) {
    var out = [], N = NaN;
    ['r', 'l'].forEach(function (k) {
      var e = crop && crop[k];
      var p = e && ((e.tb && e.dc) ? [0.65 * e.tb[0] + 0.35 * e.dc[0], 0.65 * e.tb[1] + 0.35 * e.dc[1]] : (e.tb || e.dc));
      out.push(p ? p[0] : N, p ? p[1] : N);
    });
    ['r', 'l'].forEach(function (k) { var e = crop && crop[k]; out.push(e && fin(e.upper) ? e.upper : N, e && fin(e.lower) ? e.lower : N); });
    return out;
  }

  /* Fuse pose-normalised eye-crop pupil estimates directly into MediaPipe iris coordinates (uR, vR, uL, vL)
     when consistent, reducing single-frame landmark quantisation noise before regression. */
  function fuseCropFeatures(feat, crop) {
    var cv = cropVec(crop);
    if (!feat || !feat.vec || !crop) return cv;
    var v = feat.vec;
    if (fin(cv[0]) && Math.abs(cv[0] - v[2]) < 0.18) v[2] = 0.65 * v[2] + 0.35 * cv[0];
    if (fin(cv[1]) && Math.abs(cv[1] - v[3]) < 0.18) v[3] = 0.60 * v[3] + 0.40 * cv[1];
    if (fin(cv[2]) && Math.abs(cv[2] - v[4]) < 0.18) v[4] = 0.65 * v[4] + 0.35 * cv[2];
    if (fin(cv[3]) && Math.abs(cv[3] - v[5]) < 0.18) v[5] = 0.60 * v[5] + 0.40 * cv[3];
    var mu = (v[2] + v[4]) / 2, mv = (v[3] + v[5]) / 2;
    v[10] = mu * mu; v[11] = mv * mv; v[12] = mu * mv;
    return cv;
  }

  /* Per-dot calibration sample cleaner: drops blink/occluded/tap-shake frames, trims the worst 25%
     outliers relative to the dot's median eye vector, weights surviving frames by proximity to the
     medoid, and computes a denoised median anchor vector for the dot. */
  function cleanCalibrationSamples(samples, opts) {
    opts = opts || {};
    var maxPoseJump = opts.maxPoseJump || 0.045;
    var valid = [];
    for (var i = 0; i < (samples || []).length; i++) {
      var s = samples[i];
      if (!s || !s.vec || s.blink || s.occluded) continue;
      if (i > 0 && samples[i - 1] && samples[i - 1].pose && s.pose && (samples.length > 5)) {
        var dyaw = Math.abs(s.pose.yaw - samples[i - 1].pose.yaw);
        var dpitch = Math.abs(s.pose.pitch - samples[i - 1].pose.pitch);
        if (dyaw + dpitch > maxPoseJump) continue;   // thumb tap-shake or sudden head jerk
      }
      valid.push(s);
    }
    if (valid.length < 4) {
      return { kept: valid.map(function (s) { return { feat: s, vec: s.vec, weight: 1 }; }), anchor: valid.length ? valid[valid.length >> 1].vec.slice() : null, dropped: (samples ? samples.length : 0) - valid.length };
    }
    var keys = [2, 3, 4, 5, 6, 7];
    var medK = keys.map(function (k) { return median(valid.map(function (s) { return s.vec[k]; }).filter(fin)); });
    var dists = valid.map(function (s) {
      var ss = 0;
      for (var j = 0; j < keys.length; j++) {
        var d = (s.vec[keys[j]] || 0) - medK[j];
        ss += d * d;
      }
      return Math.sqrt(ss);
    });
    var mad = Math.max(0.006, 1.4826 * median(dists));
    var indexed = valid.map(function (s, idx) { return { feat: s, vec: s.vec, d: dists[idx] }; });
    indexed.sort(function (a, b) { return a.d - b.d; });
    var keepN = valid.length >= 6 ? Math.max(4, Math.ceil(valid.length * (opts.keepFrac || 0.72))) : valid.length;
    var kept = indexed.slice(0, keepN).map(function (item) {
      var u = item.d / (2.0 * mad);
      return { feat: item.feat, vec: item.vec, weight: 1 / (1 + u * u) };
    });
    var dim = kept[0].vec.length, anchor = new Array(dim);
    for (var c = 0; c < dim; c++) {
      var vals = kept.map(function (k) { return k.vec[c]; }).filter(fin);
      anchor[c] = vals.length ? median(vals) : NaN;
    }
    return { kept: kept, anchor: anchor, dropped: (samples ? samples.length : 0) - kept.length };
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
  var LAMBDAS_CV = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000];

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
    this.lambdaSel = opts.lambdaSel || null;  // 'cv' | 'gcv'; default: cv when crop features are present
  }
  GazeRegressor.prototype._f = function (vec) {
    if (!this.features) return vec;
    return this.features.map(function (i) { return vec[i]; });
  };
  GazeRegressor.prototype.addCalibration = function (vec, x, y, w, group) {
    this.cal.push({ f: this._f(vec), x: x, y: y, w: w == null ? 1 : w, group: group, t: Date.now() });
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
    if (this.cal.length >= 8) return this.cal.slice();
    return this.cal.concat(this.implicit.map(function (s) {
      var age = Math.max(0, t0 - s.t);
      return { f: s.f, x: s.x, y: s.y, w: s.w * Math.pow(0.5, age / self.halfLifeMs), group: s.group };
    }));
  };
  GazeRegressor.prototype.fit = function (nowT) {
    var rows = this._rows(nowT);
    if (rows.length < 8) return (this.model = null);
    if (this.mode === 'ridge') { this.model = ridgeFit(rows, null, LAMBDAS); if (this.model) this.model.kind = 'ridge'; return this.model; }
    // stage 1: weighted affine map (light ridge) of the geometric estimate
    var geo = ridgeFit(rows, GEO_IDX, [1e-3]);
    if (!geo) return (this.model = null);
    var hasCrop = !this.eyeIdx && rows.filter(function (r) { return r.f.length > 23 && (fin(r.f[23]) || fin(r.f[25])); }).length >= 6;
    var eidx = this.eyeIdx || (hasCrop ? EYE_IDX.concat(CROP_IDX) : EYE_IDX);
    var sel = this.lambdaSel || (hasCrop ? 'cv' : 'gcv');
    var resid = rows.map(function (r) { var g = ridgePredict(geo, r.f); return { f: r.f, x: r.x - g.x, y: r.y - g.y, w: r.w, group: r.group }; });
    var groups = cvGroups(rows);
    var cv = sel === 'cv' ? cvLambda(resid, eidx, LAMBDAS_CV, groups) : null;
    var eye = cv ? ridgeFit(resid, eidx, [cv.lambdaX], [cv.lambdaY]) : ridgeFit(resid, eidx, LAMBDAS);
    // 1-step Huber IRLS outlier downweighting: suppress stray glances or unflagged blink transitions
    if (eye && rows.length >= 12) {
      var errs = rows.map(function (r) { var p = ridgePredict(geo, r.f), q = ridgePredict(eye, r.f); return Math.hypot(p.x + q.x - r.x, p.y + q.y - r.y); });
      var medE = Math.max(25, median(errs));
      var rwRows = rows.map(function (r, idx) {
        var e = errs[idx], huber = e > 1.75 * medE ? 1 / (1 + Math.pow(e / (2.0 * medE), 2)) : 1;
        return { f: r.f, x: r.x, y: r.y, w: r.w * huber, group: r.group };
      });
      var geo2 = ridgeFit(rwRows, GEO_IDX, [1e-3]);
      if (geo2) {
        geo = geo2;
        resid = rwRows.map(function (r) { var g = ridgePredict(geo, r.f); return { f: r.f, x: r.x - g.x, y: r.y - g.y, w: r.w, group: r.group }; });
        eye = cv ? ridgeFit(resid, eidx, [cv.lambdaX], [cv.lambdaY]) : ridgeFit(resid, eidx, LAMBDAS);
      }
    }
    if (eye && cv) eye.cvErr = cv.cvErr;
    var rss = 0, W = 0;
    rows.forEach(function (r) { var p = ridgePredict(geo, r.f), q = ridgePredict(eye, r.f); W += r.w; rss += r.w * (Math.pow(p.x + q.x - r.x, 2) + Math.pow(p.y + q.y - r.y, 2)); });
    this.model = { kind: 'hybrid', geo: geo, eye: eye, lambda: eye ? eye.lambda : null, lambdaX: eye ? eye.lambdaX : null, lambdaY: eye ? eye.lambdaY : null, crop: hasCrop, lambdaSel: cv ? 'cv' : 'gcv', n: rows.length, rmsPx: Math.sqrt(rss / W), bias: { x: 0, y: 0 } };
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
    var dxList = [], dyList = [], ws = [];
    recent.forEach(function (s) {
      var age = Math.max(0, t0 - s.t), w = Math.pow(0.5, age / (self.halfLifeMs / 4)) * (0.6 + 0.4 * (++k / recent.length));
      var p = self._predictRaw(s.f);
      dxList.push(s.x - p.x); dyList.push(s.y - p.y); ws.push(w);
    });
    var medX = median(dxList), medY = median(dyList);
    for (var i = 0; i < recent.length; i++) {
      var d = Math.hypot(dxList[i] - medX, dyList[i] - medY);
      var rw = ws[i] / (1 + Math.pow(d / 140, 2));
      sx += rw * dxList[i]; sy += rw * dyList[i]; sw += rw;
    }
    var shrink = sw / (sw + 1.8);
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

  function fin(v) { return typeof v === 'number' && v === v && v !== Infinity && v !== -Infinity; }
  function ridgePredict(m, f) {
    var x = m.mx, y = m.my, idx = m.idx;
    for (var a = 0; a < idx.length; a++) {
      var v = f[idx[a]]; if (!fin(v)) continue;          // missing feature (e.g. crop stage off) = mean
      var z = (v - m.mu[a]) / m.sd[a]; x += z * m.wx[a]; y += z * m.wy[a];
    }
    return { x: x, y: y };
  }

  /* Lambda by grouped cross-validation: leave out all frames of one calibration target region at a
     time (targets binned on a 3x3 grid, so 9-dot calibration = leave-one-dot-out). Frames at the same
     dot are strongly correlated, which makes per-frame GCV pick too little regularisation. Scored like
     validation: error of the median prediction per held-out group. */
  function cvGroups(rows) {
    var x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    rows.forEach(function (r) { x0 = Math.min(x0, r.x); x1 = Math.max(x1, r.x); y0 = Math.min(y0, r.y); y1 = Math.max(y1, r.y); });
    var cell = function (v, a, b) { return b - a < 1 ? 0 : Math.min(2, Math.floor(3 * (v - a) / (b - a + 1e-9))); };
    return rows.map(function (r) { return r.group != null ? r.group : (cell(r.y, y0, y1) * 3 + cell(r.x, x0, x1)); });
  }
  function cvLambda(rows, idx, lambdas, groups) {   // groups: fold id per row (default: cvGroups(rows))
    var g = groups || cvGroups(rows), keys = [];
    g.forEach(function (k) { if (keys.indexOf(k) < 0) keys.push(k); });
    if (keys.length < 4) return null;
    var err = lambdas.map(function () { return 0; });
    var errX = lambdas.map(function () { return 0; });
    var errY = lambdas.map(function () { return 0; });
    keys.forEach(function (k) {
      var tr = rows.filter(function (_, i) { return g[i] !== k; }), te = rows.filter(function (_, i) { return g[i] === k; });
      var P = ridgePrep(tr, idx); if (!P) return;
      lambdas.forEach(function (lam, li) {
        var m = P.model(lam, lam), ex = [], ey = [];
        te.forEach(function (r) { var q = ridgePredict(m, r.f); ex.push(q.x - r.x); ey.push(q.y - r.y); });
        var mx = Math.abs(median(ex)), my = Math.abs(median(ey));
        errX[li] += mx; errY[li] += my;
        err[li] += Math.hypot(mx, my);
      });
    });
    var bi = 0, bx = 0, by = 0;
    err.forEach(function (e, i) { if (e < err[bi]) bi = i; });
    errX.forEach(function (e, i) { if (e < errX[bx]) bx = i; });
    errY.forEach(function (e, i) { if (e < errY[by]) by = i; });
    return { lambda: lambdas[bi], lambdaX: lambdas[bx], lambdaY: lambdas[by], cvErr: Math.hypot(errX[bx], errY[by]) / keys.length };
  }
  function median(a) { var s = a.slice().sort(function (p, q) { return p - q; }), n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : 0; }

  /* Weighted ridge over columns idx (null = all), standardised, intercept unpenalised,
     decoupled lambda_x / lambda_y chosen from `lambdas` by generalised cross-validation. */
  function ridgeFit(rowsIn, idx, lambdasX, lambdasY) {
    var P = ridgePrep(rowsIn, idx);
    if (!P) return null;
    var lxList = lambdasX || LAMBDAS, lyList = lambdasY || lxList;
    var bestX = null, bestY = null;
    lxList.forEach(function (lam) { var m = P.model(lam, lam); if (!bestX || m.gcvX < bestX.gcvX) bestX = m; });
    lyList.forEach(function (lam) { var m = P.model(lam, lam); if (!bestY || m.gcvY < bestY.gcvY) bestY = m; });
    return P.model(bestX.lambdaX, bestY.lambdaY);
  }
  function ridgePrep(rowsIn, idx) {
    var rows = rowsIn;
    var n = rows.length;
    if (!n) return null;
    idx = idx || rows[0].f.map(function (_, q) { return q; });
    rows = rows.map(function (r) { return { f: idx.map(function (q) { return r.f[q]; }), x: r.x, y: r.y, w: r.w }; });
    var p = idx.length, i, j, k;
    var W = 0, mu = new Array(p).fill(0), mx = 0, my = 0;
    var wq = new Array(p).fill(0);   // per-feature weight of rows where it is present (missing = NaN/undefined)
    rows.forEach(function (r) { W += r.w; mx += r.w * r.x; my += r.w * r.y; for (var q = 0; q < p; q++) if (fin(r.f[q])) { mu[q] += r.w * r.f[q]; wq[q] += r.w; } });
    mx /= W; my /= W; for (j = 0; j < p; j++) mu[j] = wq[j] ? mu[j] / wq[j] : 0;
    var sd = new Array(p).fill(0);
    rows.forEach(function (r) { for (var q = 0; q < p; q++) if (fin(r.f[q])) sd[q] += r.w * Math.pow(r.f[q] - mu[q], 2); });
    for (j = 0; j < p; j++) sd[j] = Math.sqrt(sd[j] / (wq[j] || 1)) || 1;
    // Z = sqrt(w) * standardised features (missing -> 0, i.e. the mean)
    var Z = rows.map(function (r) { var s = Math.sqrt(r.w); return r.f.map(function (v, q) { return fin(v) ? s * (v - mu[q]) / sd[q] : 0; }); });
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
    var model = function (lamX, lamY) {
      if (lamY == null) lamY = lamX;
      var wx = new Array(p).fill(0), wy = new Array(p).fill(0), dfX = 0, dfY = 0;
      for (j = 0; j < p; j++) {
        var dj = Math.max(d[j], 0);
        var gx = 1 / (dj + lamX), gy = 1 / (dj + lamY);
        dfX += dj * gx; dfY += dj * gy;
        for (i = 0; i < p; i++) { wx[i] += V[i][j] * gx * px[j]; wy[i] += V[i][j] * gy * py[j]; }
      }
      var rssX = 0, rssY = 0;
      for (k = 0; k < n; k++) {
        var ex = tx[k], ey = ty[k];
        for (i = 0; i < p; i++) { ex -= Z[k][i] * wx[i]; ey -= Z[k][i] * wy[i]; }
        rssX += ex * ex; rssY += ey * ey;
      }
      var gcvX = n * rssX / Math.pow(Math.max(1, n - dfX), 2);
      var gcvY = n * rssY / Math.pow(Math.max(1, n - dfY), 2);
      var rss = rssX + rssY, df = (dfX + dfY) / 2;
      return { idx: idx, mu: mu, sd: sd, mx: mx, my: my, wx: wx, wy: wy, lambda: lamX, lambdaX: lamX, lambdaY: lamY, df: df, gcv: gcvX + gcvY, gcvX: gcvX, gcvY: gcvY, n: n, rmsPx: Math.sqrt(rss / W) };
    };
    return { model: model };
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
    var dist = feat.distanceCm, lo = mobile ? 18 : 33, hi = mobile ? 62 : 85;
    checks.push(dist == null ? { key: 'distance', ok: true, label: 'Distance unknown' } :
      dist < lo ? { key: 'distance', ok: false, label: 'Too close (~' + Math.round(dist) + ' cm)', hint: 'Move back a little.' } :
      dist > hi ? { key: 'distance', ok: false, label: 'Too far (~' + Math.round(dist) + ' cm)', hint: mobile ? 'Hold the phone a bit closer.' : 'Move a little closer to the screen.' } :
      { key: 'distance', ok: true, label: 'Distance ~' + Math.round(dist) + ' cm' });
    var cx = feat.face.x, cy = feat.face.y;
    var tolX = mobile ? 0.24 : 0.2, tolY = mobile ? 0.28 : 0.25;
    var centred = Math.abs(cx - 0.5) < tolX && Math.abs(cy - 0.5) < tolY;
    checks.push({ key: 'centre', ok: centred, label: centred ? 'Face centred' : 'Off centre',
      hint: Math.abs(cx - 0.5) >= tolX ? 'Move so your face is in the middle of the preview.' : (cy < 0.5 ? (mobile ? 'Tilt the phone up slightly.' : 'Lower the camera or sit up.') : (mobile ? 'Tilt the phone down slightly.' : 'Raise the screen or sit lower.')) });
    var yaw = deg(feat.pose.yaw), pitch = deg(feat.pose.pitch), roll = deg(feat.pose.roll);
    var maxYaw = mobile ? 18 : 15, maxPitch = mobile ? 24 : 18;
    var facing = Math.abs(yaw) < maxYaw && Math.abs(pitch) < maxPitch;
    checks.push({ key: 'facing', ok: facing, label: facing ? 'Facing the screen' : 'Turn to face the screen',
      hint: Math.abs(yaw) >= maxYaw ? 'Turn your head toward the screen.' : 'Level your chin.' });
    var level = Math.abs(roll) < (mobile ? 14 : 10);
    checks.push({ key: 'level', ok: level, label: level ? 'Head level' : 'Head tilted', hint: 'Straighten your head.' });
    checks.push({ key: 'eyes', ok: !feat.blink, label: feat.blink ? 'Eyes not visible' : 'Eyes visible', hint: 'Open your eyes, remove glare (tilt glasses).' });
    var q = opts.quality || {}, br = q.brightness != null ? q.brightness : opts.brightness;
    if (br != null) {
      // measured on the face itself, so a bright window behind the student shows up as backlight
      var dark = br < 60, blown = br > 215, flat = q.contrast != null && q.contrast < 14;
      checks.push(dark ? { key: 'light', ok: false, label: 'Face too dark', hint: 'Turn on a lamp in front of you or face a window. Helix asked the camera for auto-exposure.' }
        : blown ? { key: 'light', ok: false, label: 'Face over-exposed', hint: 'Move away from direct light or a bright lamp.' }
        : flat ? { key: 'light', ok: false, label: 'Low contrast (backlit?)', hint: 'Avoid a bright window behind you.' }
        : { key: 'light', ok: true, label: 'Lighting OK' });
    }
    if (q.glare != null && q.glare > 0.02) checks.push({ key: 'glare', ok: q.glare < 0.05, label: 'Glare on glasses', hint: 'Tilt your glasses down slightly or move the lamp to the side.' });
    if (q.faces > 1) checks.push({ key: 'faces', ok: true, label: 'Another face in view: following you (the closest face)', hint: '' });
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

  /* ---------- fixations (I-DT / I-VT) ----------
     Reading attention should count where the eyes *rest*, not every noisy sample in between.
     samples: [{t (ms), x, y}] in time order. Returns [{x, y, start, end, dur, n}].
     I-DT (dispersion threshold, Salvucci & Goldberg 2000) is the default because webcam
     estimates are too noisy for velocity thresholds at 15-30 Hz; dispersionPx should scale with
     the measured precision. */
  function detectFixations(samples, opts) {
    opts = opts || {};
    var method = opts.method || 'idt', minMs = opts.minMs == null ? 100 : opts.minMs, out = [];
    var emit = function (pts) {
      if (pts.length < 2) return;
      var dur = pts[pts.length - 1].t - pts[0].t;
      if (dur < minMs) return;
      var sx = 0, sy = 0; pts.forEach(function (p) { sx += p.x; sy += p.y; });
      out.push({ x: sx / pts.length, y: sy / pts.length, start: pts[0].t, end: pts[pts.length - 1].t, dur: dur, n: pts.length });
    };
    if (method === 'ivt') {
      var vmax = opts.velocityPxPerS || 2500, run = [];
      for (var i = 0; i < samples.length; i++) {
        var p = samples[i], q = samples[i - 1];
        var v = q ? Math.hypot(p.x - q.x, p.y - q.y) / Math.max(1, p.t - q.t) * 1000 : 0;
        if (q && (v > vmax || p.t - q.t > 250)) { emit(run); run = []; }
        run.push(p);
      }
      emit(run);
      return out;
    }
    var det = new FixationDetector(opts);
    samples.forEach(function (p) { var f = det.push(p.t, p.x, p.y); if (f) out.push(f); });
    var last = det.flush(); if (last) out.push(last);
    return out;
  }

  /* streaming I-DT: push samples as they arrive; returns a completed fixation when one ends.
     .current() is the fixation in progress (once it has lasted minMs), or null during saccades. */
  function FixationDetector(opts) {
    opts = opts || {};
    this.disp = opts.dispersionPx || 120; this.minMs = opts.minMs == null ? 100 : opts.minMs;
    this.maxGapMs = opts.maxGapMs || 250; this.win = [];
  }
  FixationDetector.prototype._dispersion = function (pts) {
    var x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    pts.forEach(function (p) { if (p.x < x0) x0 = p.x; if (p.x > x1) x1 = p.x; if (p.y < y0) y0 = p.y; if (p.y > y1) y1 = p.y; });
    return (x1 - x0) + (y1 - y0);
  };
  FixationDetector.prototype._summary = function (pts) {
    var sx = 0, sy = 0; pts.forEach(function (p) { sx += p.x; sy += p.y; });
    return { x: sx / pts.length, y: sy / pts.length, start: pts[0].t, end: pts[pts.length - 1].t, dur: pts[pts.length - 1].t - pts[0].t, n: pts.length };
  };
  FixationDetector.prototype.setDispersion = function (px) { this.disp = Math.max(40, px); };
  FixationDetector.prototype.push = function (t, x, y) {
    var w = this.win, done = null, p = { t: t, x: x, y: y };
    if (w.length && t - w[w.length - 1].t > this.maxGapMs) { done = this.flush(); w = this.win; }
    w.push(p);
    if (this._dispersion(w) > this.disp) {
      var prev = w.slice(0, -1);
      if (prev.length >= 2 && prev[prev.length - 1].t - prev[0].t >= this.minMs) { done = this._summary(prev); this.win = [p]; }
      else { while (w.length > 1 && this._dispersion(w) > this.disp) w.shift(); }
    }
    return done;
  };
  FixationDetector.prototype.current = function () {
    var w = this.win;
    return w.length >= 2 && w[w.length - 1].t - w[0].t >= this.minMs ? this._summary(w) : null;
  };
  FixationDetector.prototype.flush = function () {
    var w = this.win; this.win = [];
    return w.length >= 2 && w[w.length - 1].t - w[0].t >= this.minMs ? this._summary(w) : null;
  };

  /* ---------- blinks over time ----------
     A blink is a *sudden, short* closure relative to this person's own recent openness. Looking
     down narrows the lids for seconds at a time and must not be thrown away (that is someone
     reading the bottom of the page). */
  function BlinkGate(opts) { opts = opts || {}; this.hist = []; this.winMs = opts.winMs || 3000; this.maxBlinkMs = opts.maxBlinkMs || 450; this.closedSince = 0; }
  BlinkGate.prototype.update = function (feat, t) {
    if (!feat) return false;
    var open = feat.open, h = this.hist;
    var base = h.length >= 5 ? h.slice().sort(function (a, b) { return a - b; })[Math.floor(h.length * 0.7)] : null;
    var rel = base ? open / Math.max(1e-3, base) : 1;
    var bs = feat.blinkScore, lookDown = feat.lookDown || 0;
    var closed = open < 0.015 || (rel < 0.45 && lookDown < 0.55) || (bs != null && bs > 0.75 && rel < 0.6 && lookDown < 0.45);
    if (closed) { if (!this.closedSince) this.closedSince = t; }
    else { this.closedSince = 0; h.push(open); this._t = (this._t || []); this._t.push(t); while (this._t.length && t - this._t[0] > this.winMs) { this._t.shift(); h.shift(); } }
    // a "blink" that lasts longer than a blink is the eyes narrowing (looking down, squinting): accept
    if (closed && t - this.closedSince > this.maxBlinkMs && open >= 0.015) return false;
    return closed;
  };

  /* ---------- smooth-pursuit calibration ----------
     The eyes trail a moving dot by ~100-250 ms. rows: [{t, vec}] features; path: [{t, x, y}] dot
     positions. Tries lags 0-400 ms and keeps the model that fits best. */
  function fitPursuit(rows, path, opts) {
    opts = opts || {};
    var best = null, step = opts.stepMs || 33;
    var at = function (t) {   // dot position at time t (linear interpolation)
      if (!path.length || t < path[0].t || t > path[path.length - 1].t) return null;
      var lo = 0, hi = path.length - 1;
      while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (path[mid].t <= t) lo = mid; else hi = mid; }
      var a = path[lo], b = path[hi], f = b.t > a.t ? (t - a.t) / (b.t - a.t) : 0;
      return { x: a.x + f * (b.x - a.x), y: a.y + f * (b.y - a.y) };
    };
    var maxLag = opts.maxLagMs || 400;
    // score every lag on the SAME rows (those with a dot position at every candidate lag);
    // otherwise long lags drop the early rows and win by fitting fewer points
    var t0 = path.length ? path[0].t + maxLag : 0;
    var scored = rows.filter(function (r) { return r.t >= t0; });
    if (scored.length < 20) scored = rows;
    for (var lag = 0; lag <= maxLag; lag += step) {
      var reg = new GazeRegressor(opts.regressor || {});
      scored.forEach(function (r) { var p = at(r.t - lag); if (p) reg.addCalibration(r.vec, p.x, p.y, opts.weight == null ? 1 : opts.weight); });
      var m = reg.fit();
      if (m && (!best || m.rmsPx < best.rms)) best = { lag: lag, rms: m.rmsPx, reg: reg };
    }
    if (!best) return null;
    best.pairs = rows.map(function (r) { var p = at(r.t - best.lag); return p ? { vec: r.vec, x: p.x, y: p.y } : null; }).filter(Boolean);
    return best;
  }

  /* ---------- partial occlusion ----------
     A hand, hair or a glasses frame over one eye shows up as that eye's shape departing from how
     it looked during calibration (width ratio between the eyes, openness asymmetry) or the iris
     landing outside the eye. base: eyeBaseline(features from calibration). */
  function eyeBaseline(feats) {
    var ratios = [], asym = [];
    feats.forEach(function (f) { if (f && f.eyes && f.eyes.l.width) { ratios.push(Math.log(f.eyes.r.width / f.eyes.l.width)); asym.push(f.eyes.r.open - f.eyes.l.open); } });
    if (ratios.length < 5) return null;
    var med = function (a) { var s = a.slice().sort(function (x, y) { return x - y; }); return s[s.length >> 1]; };
    return { ratio: med(ratios), asym: med(asym), n: ratios.length };
  }
  function eyeQuality(feat, base) {
    if (!feat || !feat.eyes) return { ok: false, reason: 'no_face' };
    var r = feat.eyes.r, l = feat.eyes.l;
    if (Math.abs(r.u) > 0.42 || Math.abs(l.u) > 0.42 || Math.abs(r.v) > 0.35 || Math.abs(l.v) > 0.35) return { ok: false, reason: 'iris_outside_eye' };
    if (base && l.width && r.width) {
      if (Math.abs(Math.log(r.width / l.width) - base.ratio) > 0.4) return { ok: false, reason: 'eye_shape' };
      if (Math.abs((r.open - l.open) - base.asym) > 0.22) return { ok: false, reason: 'one_eye_covered' };
    }
    return { ok: true };
  }

  /* ---------- when to recalibrate ----------
     cal: pose snapshot at calibration {yaw, pitch, distanceCm, faceX, faceY}; feat: current median.
     Returns null or {reason, label}. */
  function poseSnapshot(feats) {
    var ok = feats.filter(function (f) { return f && f.pose; });
    if (!ok.length) return null;
    var med = function (fn) { var a = ok.map(fn).filter(function (v) { return v != null && isFinite(v); }).sort(function (x, y) { return x - y; }); return a.length ? a[a.length >> 1] : null; };
    return { yaw: med(function (f) { return f.pose.yaw; }), pitch: med(function (f) { return f.pose.pitch; }), distanceCm: med(function (f) { return f.distanceCm; }),
             faceX: med(function (f) { return f.face.x; }), faceY: med(function (f) { return f.face.y; }), n: ok.length };
  }
  function recalTrigger(cal, now, opts) {
    if (!cal || !now) return null;
    opts = opts || {};
    var deg = 180 / Math.PI;
    if (cal.distanceCm && now.distanceCm) {
      var r = now.distanceCm / cal.distanceCm;
      if (r < (opts.minRatio || 0.78) || r > (opts.maxRatio || 1.28)) return { reason: 'distance', label: r < 1 ? 'You moved closer to the screen' : 'You moved further from the screen' };
    }
    if (Math.abs((now.yaw - cal.yaw) * deg) > (opts.maxYawDeg || 9) || Math.abs((now.pitch - cal.pitch) * deg) > (opts.maxPitchDeg || 9)) return { reason: 'head_turn', label: 'Your head is turned differently from calibration' };
    if (Math.hypot(now.faceX - cal.faceX, now.faceY - cal.faceY) > (opts.maxShift || 0.16)) return { reason: 'moved', label: 'You moved in front of the camera' };
    return null;
  }

  /* ---------- mobile address bar ----------
     Phones grow/shrink the viewport as the URL bar hides. With a top bar (Android Chrome) the
     page content moves up by the change in height, so gaze in calibration-time CSS px must be
     shifted; with a bottom bar (iOS Safari 15+) the top edge stays put. Returns the y offset to
     add to predictions, or null when the change is too big to be the URL bar (rotate/resize). */
  function viewportShift(cal, now, opts) {
    if (!cal || !now) return 0;
    opts = opts || {};
    if (Math.abs(now.w - cal.w) > 2) return null;                     // width changed: real resize/rotation
    var dh = now.h - cal.h;
    if (Math.abs(dh) > Math.max(140, 0.2 * cal.h)) return null;
    return opts.topBar ? dh : 0;
  }

  return { CROP: CROP, R_CONTOUR: R_CONTOUR, L_CONTOUR: L_CONTOUR, eyeCropTransform: eyeCropTransform, polygonMask: polygonMask, pupilTimmBarth: pupilTimmBarth, pupilDarkCentroid: pupilDarkCentroid, eyePatch: eyePatch, cropEyeFeatures: cropEyeFeatures,
    LM: LM, FEATURE_NAMES: FEATURE_NAMES, CROP_NAMES: CROP_NAMES, CROP_IDX: CROP_IDX, cropVec: cropVec, fuseCropFeatures: fuseCropFeatures, cleanCalibrationSamples: cleanCalibrationSamples, cvLambda: cvLambda, cvGroups: cvGroups, GEO_IDX: GEO_IDX, EYE_IDX: EYE_IDX, ridgeFit: ridgeFit, headPose: headPose, eyeFeatures: eyeFeatures,
    jacobiEigen: jacobiEigen, GazeRegressor: GazeRegressor, OrientationModels: OrientationModels,
    poseGuidance: poseGuidance, angularError: angularError, aoiResolution: aoiResolution,
    DriftTracker: DriftTracker, CM_PER_CSS_PX: CM_PER_CSS_PX, IRIS_DIAMETER_CM: IRIS_DIAMETER_CM,
    detectFixations: detectFixations, FixationDetector: FixationDetector, BlinkGate: BlinkGate, fitPursuit: fitPursuit,
    eyeBaseline: eyeBaseline, eyeQuality: eyeQuality, poseSnapshot: poseSnapshot, recalTrigger: recalTrigger, viewportShift: viewportShift };
});
