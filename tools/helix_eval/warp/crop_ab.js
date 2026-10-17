#!/usr/bin/env node
/* Offline A/B of eye-crop feature sets on warp sequences (features dumped by bench.html with the
   crop stage on). usage: node crop_ab.js <suffix> <variant,...> <seq_dir>... [--json out]
   Each variant = stage-2 feature groups + lambda selection. Mirrors GazeRegressor's hybrid model
   (stage 1 affine on the geometric estimate, stage 2 ridge on the residual) using helix-model.js. */
'use strict';
const fs = require('fs'), path = require('path');
const M = require('../../../static/js/helix/helix-model.js');
const args = process.argv.slice(2);
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : null;
const rest = args.filter((a, i, all) => a !== '--json' && all[i - 1] !== '--json');
const suffix = rest[0], variants = rest[1].split(','), dirs = rest.slice(2);
const SETTLE = 5, LAMBDAS = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000];
const med = (a) => { const s = a.filter((v) => v != null && isFinite(v)).sort((x, y) => x - y); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : null; };
const usable = (f) => f && !f.none && !f.blink && !f.occluded && f.vec && f.crop && f.crop.r && f.crop.l;

// ---- feature groups appended after the 23-dim base vec
function blockPatch(p, pw, ph, bw, bh) {   // area-average a pw x ph patch down to bw x bh
  const out = []; const sx = pw / bw, sy = ph / bh;
  for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) {
    let s = 0, n = 0;
    for (let yy = Math.floor(y * sy); yy < Math.floor((y + 1) * sy); yy++) for (let xx = Math.floor(x * sx); xx < Math.floor((x + 1) * sx); xx++) { s += p[yy * pw + xx]; n++; }
    out.push(s / n);
  }
  return out;
}
const GROUPS = {
  tb: (c) => [...(c.r.tb || c.r.dc || [0, 0]), ...(c.l.tb || c.l.dc || [0, 0])],
  dc: (c) => [...(c.r.dc || [0, 0]), ...(c.l.dc || [0, 0])],
  lid: (c) => [c.r.up, c.r.lo, c.l.up, c.l.lo].map((v) => v == null ? 0 : v),
  p5: (c) => [...blockPatch(c.r.p, 15, 9, 5, 3), ...blockPatch(c.l.p, 15, 9, 5, 3)],
  p10: (c) => [...blockPatch(c.r.p, 15, 9, 10, 6), ...blockPatch(c.l.p, 15, 9, 10, 6)],
  p15: (c) => [...c.r.p, ...c.l.p],
};
// variant syntax: groups joined by '+', optional ':pcaK' for patch groups, '@cv' grouped-CV lambda, '@gcv' (default)
// 'base' alone = pass-4 model. 'sel' = per-user choice among SEL by grouped CV.
const SELS = { sel: ['base@cv', 'base+tb+lid@cv', 'base+dc+lid@cv', 'base+tb+lid+p5@cv', 'base+p10:pca12@cv'], selA: ['base@cv', 'base+tb+lid@cv'], selB: ['base@cv', 'base+tb+lid@cv', 'base+p10:pca12@cv'], selG: ['base', 'base@cv'] };
function parse(v) {
  const [g, sel] = v.split('@'); const parts = g.split('+');
  return { name: v, groups: parts.filter((x) => x !== 'base' && x !== 'noeye').map((x) => { const [n, pc] = x.split(':'); return { n, pca: pc ? +pc.replace('pca', '') : 0 }; }),
    noEye: parts.includes('noeye'), lam: sel || 'gcv' };
}

function pcaFit(X, k) {   // top-k principal axes by power iteration with deflation
  const n = X.length, p = X[0].length, mu = new Array(p).fill(0);
  X.forEach((r) => r.forEach((v, j) => { mu[j] += v / n; }));
  const C = X.map((r) => r.map((v, j) => v - mu[j]));
  const comps = [];
  for (let c = 0; c < k; c++) {
    let w = Array.from({ length: p }, (_, j) => Math.sin(j * 1.7 + c + 1));
    for (let it = 0; it < 60; it++) {
      const s = C.map((r) => r.reduce((a, v, j) => a + v * w[j], 0));
      const nw = new Array(p).fill(0); C.forEach((r, i) => r.forEach((v, j) => { nw[j] += v * s[i]; }));
      comps.forEach((q) => { const d = nw.reduce((a, v, j) => a + v * q[j], 0); for (let j = 0; j < p; j++) nw[j] -= d * q[j]; });
      const nn = Math.hypot(...nw) || 1; w = nw.map((v) => v / nn);
    }
    comps.push(w);
  }
  return { mu, comps, proj: (x) => comps.map((q) => q.reduce((a, v, j) => a + v * (x[j] - mu[j]), 0)) };
}

function buildModel(rows, cfg) {   // rows: {vec, crop, x, y, w}
  // assemble extended feature vectors
  const extras = cfg.groups.map((g) => ({ g, raw: rows.map((r) => GROUPS[g.n](r.crop)) }));
  const pcas = extras.map((e) => e.g.pca ? pcaFit(e.raw, e.g.pca) : null);
  const featOf = (vec, crop) => { let f = vec.slice(); cfg.groups.forEach((g, i) => { const raw = GROUPS[g.n](crop); f = f.concat(pcas[i] ? pcas[i].proj(raw) : raw); }); return f; };
  const R = rows.map((r) => ({ f: featOf(r.vec, r.crop), x: r.x, y: r.y, w: r.w, key: r.key }));
  const geo = M.ridgeFit(R, M.GEO_IDX, [1e-3]);
  const resid = R.map((r) => { const g = pred1(geo, r.f); return { f: r.f, x: r.x - g.x, y: r.y - g.y, w: r.w, key: r.key }; });
  const idx = (cfg.noEye ? [] : M.EYE_IDX.slice()).concat(Array.from({ length: R[0].f.length - 23 }, (_, i) => 23 + i));
  let lam, cvErr = null;
  if (cfg.lam === 'cvgcv') { cfg = Object.assign({}, cfg, { lam: 'cvfix', fixLam: M.ridgeFit(resid, idx, LAMBDAS.slice(0, 9)).lambda }); }
  if (cfg.lam === 'cv' || cfg.lam === 'cvfix') {
    const keys = [...new Set(resid.map((r) => r.key))];
    let best = null;
    for (const l of (cfg.lam === 'cvfix' ? [cfg.fixLam] : LAMBDAS)) {
      let se = 0, sw = 0;
      for (const k of keys) {
        const tr = resid.filter((r) => r.key !== k), te = resid.filter((r) => r.key === k);
        const m = M.ridgeFit(tr, idx, [l]);
        // per-group error on the group's median prediction (matches how validation is scored)
        const px = med(te.map((r) => pred1(m, r.f).x - r.x)), py = med(te.map((r) => pred1(m, r.f).y - r.y));
        se += Math.hypot(px, py); sw++;
      }
      if (!best || se / sw < best.e) best = { e: se / sw, l };
    }
    lam = [best.l]; cvErr = best.e;
  } else lam = LAMBDAS.slice(0, 9);
  const eye = M.ridgeFit(resid, idx, lam);
  return { cvErr, lambda: eye.lambda, predict: (vec, crop) => { const f = featOf(vec, crop), a = pred1(geo, f), b = pred1(eye, f); return { x: a.x + b.x, y: a.y + b.y }; } };
}
function pred1(m, f) { let x = m.mx, y = m.my; for (let a = 0; a < m.idx.length; a++) { const z = (f[m.idx[a]] - m.mu[a]) / m.sd[a]; x += z * m.wx[a]; y += z * m.wy[a]; } return { x, y }; }

function evalSeq(d, vnames) {
  const truth = JSON.parse(fs.readFileSync(path.join(d, 'truth.json'))), T = truth.truth;
  const feat = JSON.parse(fs.readFileSync(path.join(d, `features${suffix}.json`))), F = feat.frames;
  const rows = [];
  T.forEach((t, k) => { if (t.phase === 'cal' && t.j >= SETTLE && usable(F[k])) rows.push({ vec: F[k].vec, crop: F[k].crop, x: t.target[0], y: t.target[1], w: 1, key: t.target.join(',') }); });
  const score = (model, phase) => {
    const pts = new Map();
    T.forEach((t, k) => { if (t.phase !== phase || t.j < SETTLE || !usable(F[k])) return; const p = model.predict(F[k].vec, F[k].crop), key = t.target.join(',');
      if (!pts.has(key)) pts.set(key, { t: t.target, D: t.D, xs: [], ys: [] }); pts.get(key).xs.push(p.x); pts.get(key).ys.push(p.y); });
    const degs = [], dx = [], dy = [];
    pts.forEach((v) => { const ex = med(v.xs) - v.t[0], ey = med(v.ys) - v.t[1]; degs.push(M.angularError(Math.hypot(ex, ey), v.D, truth.cmPerPx)); dx.push(M.angularError(Math.abs(ex), v.D, truth.cmPerPx)); dy.push(M.angularError(Math.abs(ey), v.D, truth.cmPerPx)); });
    return { deg: med(degs), hDeg: med(dx), vDeg: med(dy) };
  };
  const out = { subject: truth.subject, cond: path.basename(d), cropMs: feat.cropMs, inferMs: feat.inferMs, v: {} };
  const built = {};
  for (const vn of vnames) {
    if (SELS[vn]) {
      const SEL = SELS[vn];
      const cands = SEL.map((s) => { if (!built[s] || built[s].cvErr == null) built[s] = buildModel(rows, parse(s.includes('@') ? s : s + '@cvgcv')); return built[s]; });
      const bi = cands.reduce((b, m, i) => m.cvErr < cands[b].cvErr ? i : b, 0);
      out.v[vn] = Object.assign(score(cands[bi], 'val'), { pick: SEL[bi] });
      if (T.some((t) => t.phase === 'val2')) out.v[vn].moved = score(cands[bi], 'val2').deg;
      continue;
    }
    const m = built[vn] || (built[vn] = buildModel(rows, parse(vn)));
    out.v[vn] = Object.assign(score(m, 'val'), { lambda: m.lambda });
    if (T.some((t) => t.phase === 'val2')) out.v[vn].moved = score(m, 'val2').deg;
  }
  return out;
}

const res = dirs.map((d) => evalSeq(d, variants));
const f2 = (v) => v == null ? '—' : v.toFixed(2);
console.log('| subject | cond | ' + variants.join(' | ') + ' |'); console.log('|---|---|' + variants.map(() => '---').join('|') + '|');
res.forEach((r) => console.log(`| ${r.subject} | ${r.cond} | ` + variants.map((v) => f2(r.v[v].deg) + (r.v[v].pick ? ' (' + r.v[v].pick + ')' : '')).join(' | ') + ' |'));
const summ = (sel) => variants.map((v) => f2(med(sel.map((r) => r.v[v].deg))));
console.log('| **median all** | ' + res.length + ' | ' + summ(res).join(' | ') + ' |');
console.log('| median H | | ' + variants.map((v) => f2(med(res.map((r) => r.v[v].hDeg)))).join(' | ') + ' |');
console.log('| median V | | ' + variants.map((v) => f2(med(res.map((r) => r.v[v].vDeg)))).join(' | ') + ' |');
[...new Set(res.map((r) => r.subject))].forEach((s) => console.log(`| ${s} | median | ` + summ(res.filter((r) => r.subject === s)).join(' | ') + ' |'));
// win counts vs first variant
console.log('| wins vs ' + variants[0] + ' | | ' + variants.map((v) => res.filter((r) => r.v[v].deg < r.v[variants[0]].deg).length + '/' + res.length).join(' | ') + ' |');
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(res, null, 1));
