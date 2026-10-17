/* Synthetic landmark generator for the Helix gaze pipeline.
   A geometric eye/head model (eyeballs that rotate toward known screen targets, per-user kappa
   offsets, lids that follow vertical gaze, head pose + translation, pinhole camera above the screen)
   is projected into MediaPipe-style normalised landmarks with Gaussian landmark noise.
   This measures the feature + regression pipeline under controlled conditions. It does NOT measure
   MediaPipe's own landmark accuracy on real faces; see RESULTS.md for what that means. */
'use strict';

function rng(seed) {            // mulberry32: deterministic so results are repeatable
  let a = seed >>> 0;
  return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
function gauss(r) { let u = 0, v = 0; while (!u) u = r(); while (!v) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
function rotMat(yaw, pitch, roll) {  // R = Rz(roll) * Ry(yaw) * Rx(pitch)
  const cx = Math.cos(pitch), sx = Math.sin(pitch), cy = Math.cos(yaw), sy = Math.sin(yaw), cz = Math.cos(roll), sz = Math.sin(roll);
  const Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]], Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]];
  const mul = (A, B) => A.map((r, i) => B[0].map((_, j) => r.reduce((s, _v, k) => s + A[i][k] * B[k][j], 0)));
  return mul(Rz, mul(Ry, Rx));
}
const apply = (R, p) => [R[0][0] * p[0] + R[0][1] * p[1] + R[0][2] * p[2], R[1][0] * p[0] + R[1][1] * p[1] + R[1][2] * p[2], R[2][0] * p[0] + R[2][1] * p[1] + R[2][2] * p[2]];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]); return [a[0] / l, a[1] / l, a[2] / l]; };

/* Rotate unit vector g by small angles (dyaw about y, dpitch about x). */
function turn(g, dyaw, dpitch) { return norm(apply(rotMat(dyaw, dpitch, 0), g)); }

const DEFAULTS = {
  W: 640, H: 480, hfovDeg: 60,                   // camera
  screenW: 1440, screenH: 900, cmPerPx: 0.0213,  // ~30.7 x 19.2 cm (14" laptop panel at 1440 css px)
  camAboveScreenCm: 0.8,
  distanceCm: 55, lmNoisePx: 0.8, fixationNoiseDeg: 0.6, poseNoiseDeg: 0.8, matrixNoiseDeg: 1.0
};

function makeUser(seed, over) {
  const r = rng(seed);
  return Object.assign({}, DEFAULTS, {
    seed, r,
    kappa: [[(2 + 3 * r()) * Math.PI / 180, (gauss(r) * 1.5) * Math.PI / 180], [(-2 - 3 * r()) * Math.PI / 180, (gauss(r) * 1.5) * Math.PI / 180]],
    ipd: 6.0 + 0.6 * gauss(r),       // interpupillary distance (cm)
    eyeRadius: 1.2 + 0.05 * gauss(r),
    head: { x: gauss(r) * 2, y: 6 + gauss(r) * 2, z: DEFAULTS.distanceCm + gauss(r) * 4, yaw: gauss(r) * 0.04, pitch: 0.05 + gauss(r) * 0.04, roll: gauss(r) * 0.03 }
  }, over || {});
}

/* Screen px -> world (cm). Camera at origin looking +z toward the user; image x right, y down. */
function screenToWorld(u, sx, sy) { return [(sx - u.screenW / 2) * u.cmPerPx, u.camAboveScreenCm + sy * u.cmPerPx, 0]; }

function frame(u, target, head, opts) {
  opts = opts || {};
  const r = u.r, d2r = Math.PI / 180;
  const hp = {
    x: head.x + gauss(r) * 0.15, y: head.y + gauss(r) * 0.15, z: head.z + gauss(r) * 0.2,
    yaw: head.yaw + gauss(r) * u.poseNoiseDeg * d2r * 0.3, pitch: head.pitch + gauss(r) * u.poseNoiseDeg * d2r * 0.3, roll: head.roll + gauss(r) * u.poseNoiseDeg * d2r * 0.3
  };
  const R = rotMat(hp.yaw, hp.pitch, hp.roll), H = [hp.x, hp.y, hp.z];
  const toW = (p) => add(H, apply(R, p));
  const T = screenToWorld(u, target[0], target[1]);
  const f = u.W / (2 * Math.tan(u.hfovDeg * d2r / 2));
  const lm = new Array(478);
  const put = (i, pw) => { lm[i] = { x: (f * pw[0] / pw[2] + u.W / 2 + gauss(r) * u.lmNoisePx) / u.W, y: (f * pw[1] / pw[2] + u.H / 2 + gauss(r) * u.lmNoisePx) / u.H, z: 0 }; };
  const eyes = [  // [eyeball centre (head coords), corner idx outer/inner, lids, iris centre + ring]
    { c: [-u.ipd / 2, 0, 1.0], cor: [33, 133], up: 159, lo: 145, iris: 468, ring: [469, 471] },
    { c: [u.ipd / 2, 0, 1.0], cor: [263, 362], up: 386, lo: 374, iris: 473, ring: [474, 476] }
  ];
  const fix = [gauss(r) * u.fixationNoiseDeg * d2r, gauss(r) * u.fixationNoiseDeg * d2r];
  eyes.forEach((e, k) => {
    const C = toW(e.c);
    let g = norm([T[0] - C[0], T[1] - C[1], T[2] - C[2]]);     // visual axis toward the target
    g = turn(g, u.kappa[k][0] * (k ? 1 : 1) + fix[0], u.kappa[k][1] + fix[1]);   // optical axis = visual + kappa
    const iris = add(C, g.map((v) => v * u.eyeRadius));
    put(e.iris, iris);
    const side = apply(R, [1, 0, 0]);
    put(e.ring[0], add(iris, side.map((v) => v * 0.585))); put(e.ring[1], add(iris, side.map((v) => -v * 0.585)));
    const outerX = e.c[0] + (e.c[0] < 0 ? -1.45 : 1.45), innerX = e.c[0] + (e.c[0] < 0 ? 1.35 : -1.35);
    put(e.cor[0], toW([outerX, 0.08, 0.15])); put(e.cor[1], toW([innerX, 0.05, 0.1]));
    // lids: upper lid follows vertical gaze (in head frame), lower lid a little
    const gh = apply([[R[0][0], R[1][0], R[2][0]], [R[0][1], R[1][1], R[2][1]], [R[0][2], R[1][2], R[2][2]]], g); // head-frame gaze
    const vert = Math.asin(Math.max(-1, Math.min(1, gh[1])));
    const blink = opts.blink === 'half' ? 0.62 : opts.blink ? 0.9 : 0;   // 'half' = lids narrowed, e.g. looking down
    put(e.up, toW([e.c[0], -0.52 + 0.55 * vert + blink, -0.05])); put(e.lo, toW([e.c[0], 0.42 + 0.18 * vert, -0.05]));
  });
  put(234, toW([-7.0, 1.0, 3.0])); put(454, toW([7.0, 1.0, 3.0])); put(10, toW([0, -7.5, 1.5])); put(152, toW([0, 11, 1.5])); put(1, toW([0, 3.5, -2.3]));
  // facial transformation matrix (column-major), with its own estimation noise
  const mn = u.matrixNoiseDeg * d2r;
  const Rm = rotMat(hp.yaw + gauss(r) * mn, hp.pitch + gauss(r) * mn, hp.roll + gauss(r) * mn);
  const m = new Array(16).fill(0);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) m[j * 4 + i] = Rm[i][j];
  m[12] = hp.x + gauss(r) * 0.4; m[13] = hp.y + gauss(r) * 0.4; m[14] = -(hp.z + gauss(r) * 0.8); m[15] = 1;
  return { lm, matrix: m };
}

function grid(u, cols, rows, margin) {
  const pts = [];
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    pts.push([u.screenW * (margin + (1 - 2 * margin) * i / (cols - 1)), u.screenH * (margin + (1 - 2 * margin) * j / (rows - 1))]);
  }
  return pts;
}

module.exports = { rng, gauss, makeUser, frame, grid, screenToWorld, DEFAULTS };
