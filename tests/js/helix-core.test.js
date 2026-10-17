// Run: node --test tests/js/
const test = require('node:test');
const assert = require('node:assert');
const H = require('../../static/js/helix/helix-core.js');

function rng(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }
function gauss(r) { return Math.sqrt(-2 * Math.log(r() || 1e-9)) * Math.cos(2 * Math.PI * r()); }

test('Kalman reduces jitter around a fixation', () => {
  const r = rng(7), f = new H.GazeFilter({ bounds: { w: 1440, h: 900 } });
  let rawErr = 0, filtErr = 0, n = 0;
  for (let i = 0; i < 200; i++) {
    const x = 600 + gauss(r) * 40, y = 400 + gauss(r) * 40;
    const out = f.push(x, y);
    if (i > 20 && out.ok) { rawErr += Math.hypot(x - 600, y - 400); filtErr += Math.hypot(out.x - 600, out.y - 400); n++; }
  }
  assert.ok(n > 150);
  assert.ok(filtErr / n < rawErr / n * 0.6, `filtered ${filtErr / n} vs raw ${rawErr / n}`);
});

test('single-sample spikes are rejected as outliers', () => {
  const f = new H.GazeFilter();
  for (let i = 0; i < 10; i++) f.push(500, 300);
  const spike = f.push(1400, 50);
  assert.strictEqual(spike.ok, false);
  assert.strictEqual(spike.reason, 'outlier');
  const back = f.push(502, 301);
  assert.ok(back.ok && Math.abs(back.x - 500) < 10);
});

test('a real saccade is accepted after confirmation', () => {
  const f = new H.GazeFilter({ confirmN: 3 });
  for (let i = 0; i < 10; i++) f.push(200, 200);
  assert.strictEqual(f.push(1000, 700).ok, false);
  assert.strictEqual(f.push(1005, 702).ok, false);
  const ok = f.push(998, 699);
  assert.ok(ok.ok && ok.saccade);
  assert.ok(Math.abs(ok.x - 1001) < 5);
});

test('invalid and wildly off-screen predictions are rejected', () => {
  const f = new H.GazeFilter({ bounds: { w: 1000, h: 800 } });
  assert.strictEqual(f.push(NaN, 3).ok, false);
  assert.strictEqual(f.push(5000, 3).reason, 'out_of_range');
  assert.strictEqual(f.rejected, 2);
});

test('validation score: accurate > noisy > missing', () => {
  const vp = { w: 1440, h: 900 };
  const mk = (err, n) => [{ x: 200, y: 150 }, { x: 1240, y: 150 }, { x: 720, y: 450 }, { x: 200, y: 750 }, { x: 1240, y: 750 }]
    .map(p => ({ x: p.x, y: p.y, samples: Array.from({ length: n }, (_, i) => ({ x: p.x + err * Math.cos(i), y: p.y + err * Math.sin(i) })) }));
  const good = H.scoreValidation(mk(60, 20), vp);
  const bad = H.scoreValidation(mk(350, 20), vp);
  const none = H.scoreValidation(mk(60, 1), vp);
  assert.ok(good.score >= 85, 'good ' + good.score);
  assert.strictEqual(good.band, 'good');
  assert.ok(bad.score < 45, 'bad ' + bad.score);
  assert.strictEqual(bad.band, 'poor');
  assert.strictEqual(none.valid, false);
  assert.strictEqual(good.errorPx, 60);
});

test('AOI debouncer ignores flicker shorter than the threshold', () => {
  const d = new H.AoiDebouncer(150);
  const A = { key: 'a' }, B = { key: 'b' };
  assert.strictEqual(d.feed(A, 0).key, 'a');
  assert.strictEqual(d.feed(B, 50).key, 'a');
  assert.strictEqual(d.feed(A, 90).key, 'a');
  assert.strictEqual(d.feed(B, 100).key, 'a');
  assert.strictEqual(d.feed(B, 260).key, 'b');
});

test('state timeline: totals, buckets and segment merge', () => {
  const t = new H.StateTimeline(1000);
  t.enter({ key: 'h0', label: 'Intro' }, 1000);
  t.enter({ key: '_hidden', label: 'Tab hidden' }, 4000);
  t.enter({ key: 'h1', label: 'Body' }, 6000);
  t.enter({ key: 'h0', label: 'Intro' }, 6050); // 50ms flicker gets merged
  const snap = t.checkpoint(9000);
  assert.strictEqual(snap.totals.total, 8000);
  assert.strictEqual(snap.totals.hidden, 2000);
  assert.strictEqual(snap.totals.attentive, 6000);
  const h0 = snap.buckets.find(b => b.aoi_key === 'h0');
  assert.strictEqual(h0.dwell_ms, 3000 + 2950);
  assert.ok(snap.segments.length >= 3);
  assert.strictEqual(snap.segments[0].t0, 0);
  // checkpoint keeps the open segment going
  const snap2 = t.checkpoint(10000);
  assert.strictEqual(snap2.totals.total, 9000);
  assert.strictEqual(snap2.segments[0].aoi, 'h0');
});

test('heat grid bins fractions and ignores out-of-range', () => {
  const g = new H.HeatGrid(20, 60);
  assert.ok(g.add(0.5, 0.5, 40));
  assert.ok(!g.add(1.2, 0.5, 40));
  g.add(0.51, 0.505, 40);
  assert.deepStrictEqual(g.toJSON().cells, { '10,30': 80 });
});

test('confidence drops with lost face, dispersion and stale samples', () => {
  assert.strictEqual(H.confidence({ face: false }), 0);
  const hi = H.confidence({ face: true, dispersion: 10, diag: 1700, calibrationScore: 90, sinceSampleMs: 50 });
  const lo = H.confidence({ face: true, dispersion: 250, diag: 1700, calibrationScore: 40, sinceSampleMs: 1200 });
  assert.ok(hi > 0.8 && lo < 0.3, `${hi} ${lo}`);
});

test('batch queue: sequencing, retry with backoff, persistence', async () => {
  const store = { d: {}, getItem(k) { return this.d[k] || null; }, setItem(k, v) { this.d[k] = v; }, removeItem(k) { delete this.d[k]; } };
  let clock = 0, fail = 2; const sent = [];
  const q = new H.BatchQueue({ storage: store, key: 'k', now: () => clock,
    send: b => { if (fail-- > 0) return Promise.reject(new Error('net')); sent.push(b.seq); return Promise.resolve({ ok: true }); } });
  q.push({ a: 1 }); q.push({ a: 2 });
  assert.ok(store.d.k, 'persisted');
  assert.strictEqual(await q.flush(), false);
  assert.strictEqual(q.backoffMs(), 1000);
  assert.strictEqual(await q.flush(), false, 'still backing off');
  clock += 1000; await q.flush();
  assert.strictEqual(q.backoffMs(), 2000);
  clock += 2000; await q.flush();
  assert.deepStrictEqual(sent, [0, 1]);
  assert.strictEqual(store.d.k, undefined, 'cleared after success');
  // a fresh queue restores unsent items from storage
  store.d.k = JSON.stringify({ items: [{ seq: 5 }], seq: 6 });
  const q2 = new H.BatchQueue({ storage: store, key: 'k', send: () => Promise.resolve({ ok: true }) });
  assert.strictEqual(q2.items.length, 1);
  assert.strictEqual(q2.push({}), 6);
});
