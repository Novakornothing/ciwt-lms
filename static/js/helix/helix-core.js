/* Novak LMS Helix core — pure, DOM-free logic shared by the runtime and the tests.
   Smoothing (median outlier gate + 1D Kalman), validation scoring, AOI
   debouncing, attention state timeline, heat grid, and a retrying batch queue.
   UMD: window.HelixCore in the browser, module.exports under Node. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.HelixCore = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }
  function median(arr) {
    if (!arr.length) return NaN;
    var s = arr.slice().sort(function (a, b) { return a - b; });
    var m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  /* ---------- 1D Kalman (constant-position model) ---------- */
  function Kalman1D(q, r) {
    this.q = q == null ? 4 : q;     // process noise (px^2 per step): how fast true gaze moves
    this.r = r == null ? 900 : r;   // measurement noise (px^2): WebGazer jitter (~30px sd)
    this.x = null; this.p = 1;
  }
  Kalman1D.prototype.reset = function (z) { this.x = z; this.p = this.r; };
  Kalman1D.prototype.update = function (z) {
    if (this.x === null) { this.reset(z); return z; }
    this.p += this.q;
    var k = this.p / (this.p + this.r);
    this.x += k * (z - this.x);
    this.p *= (1 - k);
    return this.x;
  };

  /* ---------- Gaze filter: validity + median outlier gate + saccade confirm + Kalman ---------- */
  function GazeFilter(opts) {
    opts = opts || {};
    this.maxJump = opts.maxJump || 260;          // px from rolling median before a sample is "suspicious"
    this.confirmN = opts.confirmN || 3;          // consecutive agreeing suspicious samples = real saccade
    this.window = opts.window || 5;
    this.bounds = opts.bounds || null;           // {w,h}: reject wildly off-screen predictions
    this.kx = new Kalman1D(opts.q, opts.r);
    this.ky = new Kalman1D(opts.q, opts.r);
    this.raw = []; this.pendingJump = [];
    this.accepted = 0; this.rejected = 0;
  }
  GazeFilter.prototype.push = function (x, y) {
    if (typeof x !== 'number' || typeof y !== 'number' || !isFinite(x) || !isFinite(y)) {
      this.rejected++; return { ok: false, reason: 'invalid' };
    }
    if (this.bounds) {
      var mx = this.bounds.w * 0.5, my = this.bounds.h * 0.5;
      if (x < -mx || y < -my || x > this.bounds.w + mx || y > this.bounds.h + my) {
        this.rejected++; return { ok: false, reason: 'out_of_range' };
      }
    }
    var p = { x: x, y: y };
    if (this.raw.length >= 3) {
      var med = { x: median(this.raw.map(function (s) { return s.x; })),
                  y: median(this.raw.map(function (s) { return s.y; })) };
      if (dist(p, med) > this.maxJump) {
        var pj = this.pendingJump;
        if (pj.length && dist(p, pj[pj.length - 1]) > this.maxJump) pj.length = 0;
        pj.push(p);
        if (pj.length < this.confirmN) { this.rejected++; return { ok: false, reason: 'outlier' }; }
        // confirmed saccade: jump the filter to the new fixation
        var cx = pj.reduce(function (a, s) { return a + s.x; }, 0) / pj.length;
        var cy = pj.reduce(function (a, s) { return a + s.y; }, 0) / pj.length;
        this.raw = pj.slice(); this.pendingJump = [];
        this.kx.reset(cx); this.ky.reset(cy);
        this.accepted++;
        return { ok: true, x: cx, y: cy, saccade: true };
      }
    }
    this.pendingJump.length = 0;
    this.raw.push(p);
    if (this.raw.length > this.window) this.raw.shift();
    this.accepted++;
    return { ok: true, x: this.kx.update(x), y: this.ky.update(y) };
  };
  GazeFilter.prototype.dispersion = function () {
    // RMS distance of the recent raw window from its centroid (precision proxy)
    var n = this.raw.length;
    if (n < 2) return 0;
    var cx = 0, cy = 0;
    this.raw.forEach(function (s) { cx += s.x; cy += s.y; });
    cx /= n; cy /= n;
    var ss = 0;
    this.raw.forEach(function (s) { ss += (s.x - cx) * (s.x - cx) + (s.y - cy) * (s.y - cy); });
    return Math.sqrt(ss / n);
  };

  /* ---------- Validation scoring ---------- */
  // points: [{x, y, samples:[{x,y}]}]; viewport {w,h}
  function scoreValidation(points, viewport) {
    var diag = Math.hypot(viewport.w || 1, viewport.h || 1);
    var errs = [], precs = [], per = [];
    points.forEach(function (pt) {
      var s = (pt.samples || []).filter(function (q) { return isFinite(q.x) && isFinite(q.y); });
      if (s.length < 3) { per.push({ x: pt.x, y: pt.y, error: null, n: s.length }); return; }
      var d = s.map(function (q) { return Math.hypot(q.x - pt.x, q.y - pt.y); });
      var e = median(d);
      var cx = s.reduce(function (a, q) { return a + q.x; }, 0) / s.length;
      var cy = s.reduce(function (a, q) { return a + q.y; }, 0) / s.length;
      var prec = Math.sqrt(s.reduce(function (a, q) { return a + (q.x - cx) * (q.x - cx) + (q.y - cy) * (q.y - cy); }, 0) / s.length);
      errs.push(e); precs.push(prec);
      per.push({ x: pt.x, y: pt.y, error: Math.round(e), precision: Math.round(prec), n: s.length });
    });
    if (!errs.length) return { score: 0, errorPx: 0, precisionPx: 0, band: 'poor', points: per, valid: false };
    var err = errs.reduce(function (a, b) { return a + b; }, 0) / errs.length;
    var prec = precs.reduce(function (a, b) { return a + b; }, 0) / precs.length;
    var coverage = errs.length / points.length;            // penalise points with no samples
    var score = Math.round(clamp(100 * (1 - err / (0.3 * diag)), 0, 100) * coverage);
    return {
      score: score, errorPx: Math.round(err), precisionPx: Math.round(prec), points: per, valid: true,
      band: score >= 70 ? 'good' : score >= 45 ? 'fair' : 'poor'
    };
  }

  /* ---------- AOI debouncer (hysteresis against flicker) ---------- */
  function AoiDebouncer(minMs) { this.minMs = minMs == null ? 150 : minMs; this.current = null; this.cand = null; this.candT = 0; }
  AoiDebouncer.prototype.feed = function (hit, t) {
    var key = hit && hit.key;
    if (!this.current) { this.current = hit; return hit; }
    if (key === this.current.key) { this.cand = null; return this.current; }
    if (!this.cand || this.cand.key !== key) { this.cand = hit; this.candT = t; return this.current; }
    if (t - this.candT >= this.minMs) { this.current = this.cand; this.cand = null; }
    return this.current;
  };

  /* ---------- State timeline: segments, buckets, totals ---------- */
  // pass 10: camera off (unplugged / permission revoked) counts as no face; another tab holding
  // Helix and a sleeping device count as hidden. None of these is ever reading attention.
  var CATEGORY = { off_page: 'off_page', chrome: 'off_page', _idle: 'off_page', _paused: 'off_page',
                   _face_lost: 'face_lost', _camera_off: 'face_lost', _hidden: 'hidden', _other_tab: 'hidden',
                   _asleep: 'hidden', _low_conf: 'low_conf' };
  function categoryOf(key) { return CATEGORY[key] || 'attentive'; }

  function StateTimeline(t0) {
    this.t0 = t0; this.cur = null; this.pending = []; this.buckets = {};
    this.totals = { total: 0, attentive: 0, off_page: 0, face_lost: 0, hidden: 0, low_conf: 0 };
    this.minSegMs = 120;
  }
  // a = {key, label, order, kind}; t = absolute ms
  StateTimeline.prototype.enter = function (a, t) {
    if (this.cur && this.cur.key === a.key) { this.cur.n++; return; }
    this.close(t);
    this.cur = { key: a.key, label: a.label, order: a.order || 0, kind: a.kind || 'heading', t: t, n: 1, conf: a.conf || 0 };
  };
  StateTimeline.prototype.close = function (t) {
    var c = this.cur;
    if (!c) return;
    var dur = Math.max(0, t - c.t);
    this.cur = null;
    if (dur <= 0) return;
    var cat = categoryOf(c.key);
    this.totals.total += dur;
    this.totals[cat] += dur;
    var rel0 = c.t - this.t0, rel1 = t - this.t0;
    var b = this.buckets[c.key];
    if (!b) b = this.buckets[c.key] = { aoi_key: c.key, aoi_label: c.label, aoi_order: c.order, aoi_kind: cat === 'attentive' ? c.kind : 'state',
                                        dwell_ms: 0, visits: 0, first_ms: rel0, last_ms: rel1 };
    b.dwell_ms += dur;
    b.last_ms = rel1;
    if (dur >= this.minSegMs || !this.pending.length) b.visits += 1;
    // merge tiny flickers into the previous segment rather than emitting noise
    var last = this.pending[this.pending.length - 1];
    if (dur < this.minSegMs && last && last.t1 === rel0) { last.t1 = rel1; return; }
    if (last && last.aoi === c.key && rel0 - last.t1 < this.minSegMs) { last.t1 = rel1; last.n += c.n; return; }
    this.pending.push({ t0: rel0, t1: rel1, aoi: c.key, label: c.label, n: c.n, conf: Math.round((c.conf || 0) * 100) / 100 });
  };
  // Snapshot for upload: closes the open segment at t and immediately re-opens it.
  StateTimeline.prototype.checkpoint = function (t) {
    var c = this.cur;
    if (c) { this.close(t); this.cur = { key: c.key, label: c.label, order: c.order, kind: c.kind, t: t, n: 0, conf: c.conf }; }
    var segs = this.pending; this.pending = [];
    var self = this;
    return {
      segments: segs,
      buckets: Object.keys(this.buckets).map(function (k) { return self.buckets[k]; }),
      totals: JSON.parse(JSON.stringify(this.totals))
    };
  };

  /* ---------- Heat grid over the lesson body ---------- */
  function HeatGrid(cols, rows) { this.cols = cols || 20; this.rows = rows || 60; this.cells = {}; }
  HeatGrid.prototype.add = function (fx, fy, ms) {
    if (!(fx >= 0 && fx <= 1 && fy >= 0 && fy <= 1)) return false;
    var x = Math.min(this.cols - 1, Math.floor(fx * this.cols));
    var y = Math.min(this.rows - 1, Math.floor(fy * this.rows));
    var k = x + ',' + y;
    this.cells[k] = (this.cells[k] || 0) + Math.round(ms);
    return true;
  };
  HeatGrid.prototype.toJSON = function () { return { cols: this.cols, rows: this.rows, cells: this.cells }; };

  /* ---------- Confidence estimate (0..1) ---------- */
  function confidence(o) {
    if (!o.face) return 0;
    var c = 1;
    var diag = o.diag || 1500;
    c *= clamp(1 - (o.dispersion || 0) / (0.18 * diag), 0, 1);
    if (o.calibrationScore != null) c *= clamp(0.4 + o.calibrationScore / 100 * 0.6, 0.4, 1);
    if (o.sinceSampleMs != null && o.sinceSampleMs > 400) c *= clamp(1 - (o.sinceSampleMs - 400) / 1200, 0, 1);
    return Math.round(c * 100) / 100;
  }

  /* ---------- Batch queue with sequence numbers, retry/backoff, persistence ---------- */
  function BatchQueue(opts) {
    this.send = opts.send;                      // function(batch) -> Promise<{ok, ack?, duplicate?}>
    this.storage = opts.storage || null;        // localStorage-like
    this.key = opts.key || 'helix-queue';
    this.setTimer = opts.setTimeout || (typeof setTimeout !== 'undefined' ? setTimeout : null);
    this.now = opts.now || function () { return Date.now(); };
    this.maxItems = opts.maxItems || 60;
    this.items = []; this.seq = 0; this.inflight = false; this.failures = 0; this.nextTry = 0;
    this.onState = opts.onState || function () {};
    this._load();
  }
  BatchQueue.prototype._load = function () {
    if (!this.storage) return;
    try {
      var raw = JSON.parse(this.storage.getItem(this.key) || 'null');
      if (raw && raw.items) { this.items = raw.items; this.seq = raw.seq || 0; }
    } catch (e) { /* ignore */ }
  };
  BatchQueue.prototype._save = function () {
    if (!this.storage) return;
    try {
      if (this.items.length) this.storage.setItem(this.key, JSON.stringify({ items: this.items, seq: this.seq }));
      else this.storage.removeItem(this.key);
    } catch (e) { /* quota: keep in memory */ }
  };
  BatchQueue.prototype.push = function (batch) {
    batch.seq = this.seq++;
    this.items.push(batch);
    if (this.items.length > this.maxItems) {
      // keep the newest cumulative data; drop oldest *segment-only* history first
      this.items.splice(0, this.items.length - this.maxItems);
    }
    this._save();
    return batch.seq;
  };
  BatchQueue.prototype.backoffMs = function () { return Math.min(30000, 1000 * Math.pow(2, Math.max(0, this.failures - 1))); };
  BatchQueue.prototype.flush = function () {
    var self = this;
    if (this.inflight || !this.items.length) return Promise.resolve(false);
    if (this.failures && this.now() < this.nextTry) return Promise.resolve(false);
    this.inflight = true;
    var head = this.items[0];
    return Promise.resolve().then(function () { return self.send(head); }).then(function (res) {
      self.inflight = false;
      if (!res || res.ok === false) throw new Error((res && res.error) || 'rejected');
      self.items.shift(); self.failures = 0; self._save();
      self.onState({ pending: self.items.length, ok: true });
      if (self.items.length) return self.flush();
      return true;
    }).catch(function (err) {
      self.inflight = false;
      self.failures++;
      self.nextTry = self.now() + self.backoffMs();
      self.onState({ pending: self.items.length, ok: false, error: String(err && err.message || err), retryIn: self.backoffMs() });
      return false;
    });
  };
  BatchQueue.prototype.drainAll = function () { var all = this.items.slice(); return all; };
  BatchQueue.prototype.clear = function () { this.items = []; this._save(); };

  return {
    clamp: clamp, median: median, Kalman1D: Kalman1D, GazeFilter: GazeFilter,
    scoreValidation: scoreValidation, AoiDebouncer: AoiDebouncer, StateTimeline: StateTimeline,
    categoryOf: categoryOf, HeatGrid: HeatGrid, confidence: confidence, BatchQueue: BatchQueue
  };
});
