#!/usr/bin/env node
/* Score features from bench.html against the ground truth written by gen.py.
   usage: node warp_eval.js <suffix> <seq_dir>... [--json out.json]
   Uses the same helix-model.js code as the browser: 9-point and smooth-pursuit calibration,
   16-point validation on unseen targets, implicit-click recovery after head movement, and
   fixation detection on a reading phase with known fixations. */
'use strict';
const fs = require('fs'), path = require('path');
const M = require('../../../static/js/helix/helix-model.js');
const args = process.argv.slice(2);
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : null;
const suffix = args[0], dirs = args.slice(1).filter((a, i, all) => a !== '--json' && all[i - 1] !== '--json');
const SETTLE = 5;                       // frames (333 ms at 15 fps) skipped after each target onset
const med = (a) => { const s = a.filter((v) => v != null && isFinite(v)).sort((x, y) => x - y); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : null; };
const pct = (a, p) => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(p * s.length))] : null; };

const BLINK = process.env.BLINK || 'blink';
function usable(f) { return f && !f.none && !(BLINK === 'none' ? false : f[BLINK]) && !(process.env.NOOCC ? false : f.occluded) && f.vec; }

function fitFixation(F, T, phase, opts) {
  const reg = new M.GazeRegressor(opts || {});
  T.forEach((t, k) => { if (t.phase === phase && t.j >= SETTLE && usable(F[k])) reg.addCalibration(F[k].vec, t.target[0], t.target[1]); });
  reg.fit(); return reg;
}

function fitPursuit(F, T, anchors) {
  // same code the calibration UI uses: pair features with the dot position `lag` ms earlier,
  // lag chosen by best fit (the eye trails a moving target)
  const ms = (k) => k * 1000 / 15, rows = [], pathPts = [];
  T.forEach((t, k) => { if (t.phase !== 'pursuit') return; pathPts.push({ t: ms(k), x: t.target[0], y: t.target[1] }); if (t.j >= 8 && usable(F[k])) rows.push({ t: ms(k), vec: F[k].vec }); });
  const fit = M.fitPursuit(rows, pathPts, { weight: 1 });
  if (!fit) return null;
  if (anchors) {
    // the UI flow: pursuit pairs at weight 0.7 plus three fixation dots (centre, top-left, bottom-right)
    const reg = new M.GazeRegressor();
    fit.pairs.forEach((q) => reg.addCalibration(q.vec, q.x, q.y, 0.7));
    const want = anchors.map(([ax, ay]) => [ax / 100 * 1440, ay / 100 * 900]);
    const calT = [...new Set(T.filter((t) => t.phase === 'cal').map((t) => t.target.join(',')))].map((k) => k.split(',').map(Number));
    const pick = want.map((w) => calT.reduce((b, c) => Math.hypot(c[0] - w[0], c[1] - w[1]) < Math.hypot(b[0] - w[0], b[1] - w[1]) ? c : b).join(','));
    T.forEach((t, k) => { if (t.phase === 'cal' && t.j >= SETTLE && t.j < SETTLE + 10 && pick.includes(t.target.join(',')) && usable(F[k])) reg.addCalibration(F[k].vec, t.target[0], t.target[1]); });
    reg.fit();
    return Object.assign(reg, { lag: Math.round(fit.lag / (1000 / 15)) });
  }
  return Object.assign(fit.reg, { lag: Math.round(fit.lag / (1000 / 15)) });
}

function validate(reg, F, T, phase, cmPerPx) {
  if (!reg || !reg.model) return null;
  const pts = new Map(), frameErr = [];
  T.forEach((t, k) => {
    if (t.phase !== phase || t.j < SETTLE || !usable(F[k])) return;
    const p = reg.predict(F[k].vec), key = t.target.join(',');
    if (!pts.has(key)) pts.set(key, { t: t.target, D: t.D, xs: [], ys: [] });
    pts.get(key).xs.push(p.x); pts.get(key).ys.push(p.y);
    frameErr.push(Math.hypot(p.x - t.target[0], p.y - t.target[1]));
  });
  const errs = [], degs = [];
  pts.forEach((v) => { const e = Math.hypot(med(v.xs) - v.t[0], med(v.ys) - v.t[1]); errs.push(e); degs.push(M.angularError(e, v.D, cmPerPx)); });
  return { points: errs.length, errPx: Math.round(med(errs)), p90Px: Math.round(pct(errs, 0.9)), errDeg: +med(degs).toFixed(2),
           frameErrPx: Math.round(med(frameErr)), coverage: +(frameErr.length / T.filter((t) => t.phase === phase && t.j >= SETTLE).length).toFixed(2) };
}

function fixationScore(F, T, truthFix, reg) {
  if (!M.detectFixations || !reg || !reg.model || !truthFix.length) return null;
  const samples = [];
  T.forEach((t, k) => { if (t.phase === 'read' && usable(F[k])) { const p = reg.predict(F[k].vec); samples.push({ t: k * 1000 / 15, x: p.x, y: p.y }); } });
  const fx = M.detectFixations(samples, { method: 'idt', dispersionPx: 120, minMs: 100 });
  const fv = M.detectFixations(samples, { method: 'ivt', velocityPxPerS: 2500, minMs: 100 });
  const truthMs = truthFix.reduce((s, f) => s + f.n * 1000 / 15, 0);
  const lines = (list) => {   // share of fixation time assigned to the right text line (6 lines, 81 px apart)
    let ok = 0, tot = 0;
    list.forEach((f) => {
      const k0 = Math.round(f.start / (1000 / 15)), tt = T.find((t, k) => k >= k0 && t.phase === 'read');
      if (!tt) return;
      tot += f.dur; if (Math.abs(f.y - tt.target[1]) < 0.045 * 900) ok += f.dur;
    });
    return tot ? +(ok / tot).toFixed(2) : null;
  };
  return { truthFixations: truthFix.length, idt: fx.length, ivt: fv.length, idtMeanMs: Math.round(fx.reduce((s, f) => s + f.dur, 0) / (fx.length || 1)),
           truthMeanMs: Math.round(truthMs / truthFix.length), idtLineAcc: lines(fx), ivtLineAcc: lines(fv) };
}

const rows = [];
for (const d of dirs) {
  const truth = JSON.parse(fs.readFileSync(path.join(d, 'truth.json'))), T = truth.truth;
  const feat = JSON.parse(fs.readFileSync(path.join(d, `features${suffix}.json`))), F = feat.frames;
  // CROPVEC=1: rebuild the pass-5 vec (23 + 8 crop features) from dumps that predate the engine change;
  // CROPVEC=0: strip crop features (pass-4 model on the same frames)
  if (process.env.CROPVEC != null) F.forEach((f) => { if (!f || !f.vec) return; f.vec = f.vec.slice(0, 23);
    if (process.env.CROPVEC === '1' && f.crop) f.vec = f.vec.concat(M.cropVec({ r: f.crop.r && { tb: f.crop.r.tb, dc: f.crop.r.dc, upper: f.crop.r.up, lower: f.crop.r.lo }, l: f.crop.l && { tb: f.crop.l.tb, dc: f.crop.l.dc, upper: f.crop.l.up, lower: f.crop.l.lo } })); });
  const faceRate = F.filter((f) => f && !f.none).length / F.length, blinkRate = F.filter((f) => f && f.blink).length / F.length;
  const row = { subject: truth.subject, cond: truth.cond, frames: F.length, faceRate: +faceRate.toFixed(3), blinkRate: +blinkRate.toFixed(3), inferMs: feat.inferMs };
  const r9 = fitFixation(F, T, 'cal');
  row.cal9 = validate(r9, F, T, 'val', truth.cmPerPx);
  row.fitRms = r9.model ? Math.round(r9.model.rmsPx) : null;
  if (T.some((t) => t.phase === 'pursuit')) {
    const rp = fitPursuit(F, T);
    row.pursuit = validate(rp, F, T, 'val', truth.cmPerPx); if (row.pursuit) row.pursuit.lagFrames = rp.lag;
    const ra = fitPursuit(F, T, [[50, 50], [12, 14], [88, 86]]);
    row.pursuitAnchors = validate(ra, F, T, 'val', truth.cmPerPx);
  }
  if (T.some((t) => t.phase === 'val2')) row.movedNoClicks = validate(r9, F, T, 'val2', truth.cmPerPx);
  if (T.some((t) => t.phase === 'click')) {
    // implicit samples: a click ~half-way through each fixation (features 80 ms before the click)
    T.forEach((t, k) => { if (t.phase === 'click' && t.j === 6 && usable(F[k - 1])) r9.addImplicit(F[k - 1].vec, t.target[0], t.target[1], 1, Date.now()); });
    r9.fit();
    row.afterClicks = validate(r9, F, T, 'val2', truth.cmPerPx);
  }
  if (truth.fixations && truth.fixations.length) row.reading = fixationScore(F, T, truth.fixations, r9);
  rows.push(row);
}

const fmt = (v) => v ? `${v.errPx} px / ${v.errDeg}°` : '—';
console.log('| subject | condition | face | 9-pt cal → val (median px / °) | p90 px | pursuit only | pursuit + 3 dots | moved, no clicks | after 12 clicks |');
console.log('|---|---|---|---|---|---|---|---|---|');
rows.forEach((r) => console.log(`| ${r.subject} | ${r.cond} | ${Math.round(r.faceRate * 100)}% | ${fmt(r.cal9)} | ${r.cal9 ? r.cal9.p90Px : '—'} | ${fmt(r.pursuit)} | ${fmt(r.pursuitAnchors)} | ${fmt(r.movedNoClicks)} | ${fmt(r.afterClicks)} |`));
const by = (c) => rows.filter((r) => r.cond === c);
const summary = {};
[...new Set(rows.map((r) => r.cond))].forEach((c) => {
  const g = by(c);
  summary[c] = { cal9Deg: +med(g.map((r) => r.cal9 && r.cal9.errDeg)).toFixed(2), cal9Px: Math.round(med(g.map((r) => r.cal9 && r.cal9.errPx))),
    pursuitDeg: g.some((r) => r.pursuit) ? +med(g.map((r) => r.pursuit && r.pursuit.errDeg)).toFixed(2) : null,
    pursuit3Deg: g.some((r) => r.pursuitAnchors) ? +med(g.map((r) => r.pursuitAnchors && r.pursuitAnchors.errDeg)).toFixed(2) : null,
    movedNoClicksDeg: g.some((r) => r.movedNoClicks) ? +med(g.map((r) => r.movedNoClicks && r.movedNoClicks.errDeg)).toFixed(2) : null,
    afterClicksDeg: g.some((r) => r.afterClicks) ? +med(g.map((r) => r.afterClicks && r.afterClicks.errDeg)).toFixed(2) : null };
});
console.log('\nmedian over subjects:', JSON.stringify(summary));
rows.filter((r) => r.reading).forEach((r) => console.log('reading', r.subject, JSON.stringify(r.reading)));
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({ suffix, rows, summary }, null, 1));
