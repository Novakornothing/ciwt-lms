/* Try Helix: local-only gaze playground (no uploads). Also the end-to-end test harness hook:
   window.HelixTry exposes live state for tools/helix_e2e.py. */
(function () {
  'use strict';
  var E = window.HelixEngine, Calib = window.HelixCalib, Core = window.HelixCore, Model = window.HelixModel, CFG = window.HELIX_ENGINE;
  var $ = function (id) { return document.getElementById(id); };
  var T = window.HelixTry = { engine: null, preds: 0, frames: 0, lastPred: null, score: null, history: [], trailPts: [], error: null };
  var showDot = true, filt = null, drift = new Model.DriftTracker({ window: 7 });
  var dot = $('helixGazeDot'), trail = $('hxTryTrail'), tiles = Array.prototype.slice.call(document.querySelectorAll('.hx-try-tile'));

  function state(t) { $('hxTryState').textContent = t; }
  function hud() {
    if (!T.engine) return;
    var s = T.engine.stats(), rows = [
      ['Engine', s.engine + (T.engine.fallbackReason ? ' (MediaPipe failed: ' + T.engine.fallbackReason + ')' : '')],
      ['Delegate', s.delegate || '—'], ['Frame rate', (s.fps || 0).toFixed(1) + ' fps' + (s.targetFps ? ' (target ' + s.targetFps + ')' : '')],
      ['Inference', s.inferMs != null ? s.inferMs + ' ms/frame' : '—'], ['Face found', Math.round((s.faceRate || 0) * 100) + '% of frames'],
      ['Distance', s.distanceCm ? '~' + s.distanceCm + ' cm' : '—'], ['Head yaw / pitch', s.yawDeg != null ? s.yawDeg + '° / ' + s.pitchDeg + '°' : '—'],
      ['Training samples', (s.samples || 0) + ' calibration' + (s.implicit != null ? ' + ' + s.implicit + ' implicit' : '')],
      ['Model', s.lambda != null ? 'ridge λ=' + s.lambda + (s.lambdaSel === 'cv' ? ' (grouped CV)' : ' (GCV)') + (s.modelCrop ? ' + eye-crop features' : '') + ', fit RMS ' + s.fitRmsPx + ' px' : '—'], ['Orientation', s.orientation || '—'],
      ['Camera', s.resolution || '—'], ['Eye-crop stage', s.crop || '—'],
      ['Implicit error (median)', drift.median() != null ? Math.round(drift.median()) + ' px' : '—'],
      ['Gaze estimates', T.preds + ' (' + (T.lastPred ? Math.round(T.lastPred.x) + ', ' + Math.round(T.lastPred.y) : '—') + ')']
    ];
    $('hxTryHud').innerHTML = rows.map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + String(r[1]).replace(/</g, '&lt;') + '</dd>'; }).join('');
  }
  setInterval(hud, 500);

  /* debug view of the second-stage eye crops: pose-normalised full-resolution crops of both eyes with
     the lid contour, Timm & Barth pupil (red cross) and dark-centroid estimate (blue ring). Local only. */
  function drawCrops() {
    var c = $('hxTryCrops'), cs = T.engine && T.engine.lastCrops;
    if (c && (!cs || !cs.r)) { $('hxTryCropsWrap').hidden = true; return; }
    if (!c) return;
    var W = Model.CROP.W, H = Model.CROP.H, Z = 2, g = c.getContext('2d');
    if (c.width !== 2 * W * Z + 8) { c.width = 2 * W * Z + 8; c.height = H * Z; }
    $('hxTryCropsWrap').hidden = false;
    var img = g.createImageData(W, H), tmp = drawCrops.tmp || (drawCrops.tmp = document.createElement('canvas'));
    tmp.width = W; tmp.height = H;
    g.fillStyle = '#0f172a'; g.fillRect(0, 0, c.width, c.height);
    ['r', 'l'].forEach(function (k, i) {
      var e = cs[k]; if (!e) return;
      for (var p = 0; p < W * H; p++) { var v = e.gray[p]; img.data[4 * p] = img.data[4 * p + 1] = img.data[4 * p + 2] = v; img.data[4 * p + 3] = 255; }
      tmp.getContext('2d').putImageData(img, 0, 0);
      var ox = i * (W * Z + 8);
      g.imageSmoothingEnabled = false; g.drawImage(tmp, ox, 0, W * Z, H * Z);
      g.strokeStyle = 'rgba(250,204,21,.85)'; g.lineWidth = 1.5; g.beginPath();
      e.poly.forEach(function (q, j) { var x = ox + q[0] * Z, y = q[1] * Z; if (j) g.lineTo(x, y); else g.moveTo(x, y); }); g.closePath(); g.stroke();
      var ew = W / Model.CROP.SPAN, P = function (n) { return [ox + (W / 2 + n[0] * ew) * Z, (H / 2 + n[1] * ew) * Z]; };
      if (e.dc) { var d = P(e.dc); g.strokeStyle = '#38bdf8'; g.lineWidth = 2; g.beginPath(); g.arc(d[0], d[1], 6, 0, 2 * Math.PI); g.stroke(); }
      if (e.tb) { var t = P(e.tb); g.strokeStyle = '#ef4444'; g.lineWidth = 2; g.beginPath(); g.moveTo(t[0] - 7, t[1]); g.lineTo(t[0] + 7, t[1]); g.moveTo(t[0], t[1] - 7); g.lineTo(t[0], t[1] + 7); g.stroke(); }
    });
  }
  setInterval(drawCrops, 200);

  function drawTrail() {
    var c = trail, g = c.getContext('2d');
    if (c.width !== innerWidth || c.height !== innerHeight) { c.width = innerWidth; c.height = innerHeight; }
    g.clearRect(0, 0, c.width, c.height);
    if (!showDot) return;
    var pts = T.trailPts, n = pts.length;
    for (var i = 1; i < n; i++) {
      g.strokeStyle = 'rgba(56,189,248,' + (i / n * 0.6) + ')'; g.lineWidth = 3;
      g.beginPath(); g.moveTo(pts[i - 1].x, pts[i - 1].y); g.lineTo(pts[i].x, pts[i].y); g.stroke();
    }
  }
  function onFrame(ev) {
    T.frames++;
    if (!ev.pred) return;
    var f = filt.push(ev.pred.x, ev.pred.y);
    if (!f.ok) return;
    T.preds++; T.lastPred = { x: f.x, y: f.y, t: ev.t };
    T.history.push({ x: Math.round(f.x), y: Math.round(f.y), t: ev.t }); if (T.history.length > 600) T.history.shift();
    T.trailPts.push({ x: f.x, y: f.y }); if (T.trailPts.length > 24) T.trailPts.shift();
    if (showDot) { dot.style.display = 'block'; dot.style.transform = 'translate(' + (f.x - 9) + 'px,' + (f.y - 9) + 'px)'; }
    drawTrail();
    tiles.forEach(function (t) {
      var r = t.getBoundingClientRect();
      t.classList.toggle('hot', f.x >= r.left && f.x <= r.right && f.y >= r.top && f.y <= r.bottom);
    });
  }

  function showResult(s) {
    T.score = s;
    $('hxTryResult').innerHTML = s.valid
      ? '<p class="display-6 mb-0">' + s.errorPx + ' px</p><p class="mb-2">median error' + (s.errorDeg != null ? ' \u2248 <strong>' + s.errorDeg + '\u00b0</strong> visual angle' : '') + (s.distanceCm ? ' at ~' + s.distanceCm + ' cm' : '') + '</p>' +
        '<ul class="small mb-0"><li>Score ' + s.score + '% (' + s.band + ')</li><li>Spread (precision) ' + s.precisionPx + ' px</li><li>AOI resolution supported: <strong>' + s.resolution + '</strong></li><li>Engine: ' + s.engine + ' / ' + (s.delegate || '—') + '</li></ul>'
      : '<p class="mb-0">No gaze estimates during the check \u2014 the camera could not see your eyes.</p>';
  }

  function calibrate(quick) {
    state('Calibrating\u2026');
    return Calib.run(T.engine, { quick: quick, skipPositioning: quick, minAccuracy: 0, goLabel: 'Start tracking', allowPassive: false, onValidated: showResult })
      .then(function (r) {
        if (r.action === 'cancel') { state(T.engine.ready() ? 'Tracking (calibration cancelled)' : 'Calibration cancelled'); return; }
        filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
        state('Tracking \u2014 look around the tiles');
      });
  }

  function start() {
    $('hxTryStart').disabled = true; state('Loading gaze engine\u2026');
    var prefer = $('hxTryEngine').value;
    var qd = new URLSearchParams(location.search).get('delegate');
    // eye-crop HUD: computed for display only; ?crop=1 also feeds the crop features to the model (experimental)
    var qc = new URLSearchParams(location.search).get('crop');
    E.create(Object.assign({ prefer: prefer, delegate: qd === 'CPU' ? 'CPU' : null, crop: qc === '1' ? true : qc === '0' ? false : 'view' }, CFG)).then(function (engine) {
      T.engine = engine; engine.keepCrops = true; state('Waiting for camera permission\u2026');
      return engine.start();
    }).then(function (engine) {
      filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
      engine.on(onFrame);
      ['hxTryRecal', 'hxTryDot', 'hxTryStop'].forEach(function (id) { $(id).disabled = false; });
      return calibrate(false);
    }).catch(function (err) {
      T.error = String(err && err.message || err);
      state('Could not start: ' + T.error); $('hxTryStart').disabled = false;
    });
  }

  function drawDrift() {
    var pts = drift.points, svg = $('hxTryDrift');
    if (!pts.length) { svg.innerHTML = ''; return; }
    var max = Math.max(200, Math.max.apply(null, pts.map(function (p) { return p.err; })));
    var x = function (i) { return pts.length < 2 ? 150 : 6 + i * 288 / (pts.length - 1); }, y = function (v) { return 64 - v / max * 58; };
    svg.innerHTML = '<polyline fill="none" stroke="#94a3b8" stroke-width="1" points="' + pts.map(function (p, i) { return x(i) + ',' + y(p.err); }).join(' ') + '"/>' +
      '<polyline fill="none" stroke="#0ea5e9" stroke-width="2.5" points="' + pts.map(function (p, i) { return x(i) + ',' + y(p.med); }).join(' ') + '"/>' +
      pts.map(function (p, i) { return '<circle cx="' + x(i) + '" cy="' + y(p.err) + '" r="2.5" fill="#0f172a"><title>' + p.err + ' px</title></circle>'; }).join('') +
      '<text x="4" y="10" font-size="9" fill="#64748b">' + Math.round(max) + ' px</text>';
  }

  document.addEventListener('pointerdown', function (e) {
    if (!T.engine || !T.engine.ready() || document.getElementById('helixCalib')) return;
    var tile = e.target.closest && e.target.closest('.hx-try-tile');
    if (!tile) return;
    var r = tile.getBoundingClientRect();
    var res = T.engine.implicit(r.left + r.width / 2, r.top + r.height / 2, e.pointerType === 'touch' ? 'tap' : 'click');
    if (res && res.accepted) { drift.add(res.err, Date.now(), 'click'); drawDrift(); }
  }, true);

  // orientation: phones need one model per orientation; switch or ask for a quick 5-point refresh
  var lastKey = E.orientationKey();
  window.addEventListener('resize', function () {
    var k = E.orientationKey();
    if (k === lastKey || !T.engine) return;
    lastKey = k;
    filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
    if (T.engine.setOrientation(k)) state('Rotated: using your ' + k + ' calibration');
    else { state('Rotated to ' + k + ': quick 5-point calibration'); setTimeout(function () { calibrate(true); }, 400); }
  });

  $('hxTryStart').addEventListener('click', start);
  $('hxTryRecal').addEventListener('click', function () { calibrate(false); });
  $('hxTryDot').addEventListener('click', function () {
    showDot = !showDot; this.setAttribute('aria-pressed', String(showDot)); this.textContent = showDot ? 'Hide gaze dot' : 'Show gaze dot';
    if (!showDot) dot.style.display = 'none'; drawTrail();
  });
  $('hxTryStop').addEventListener('click', function () {
    if (T.engine) T.engine.stop(); T.engine = null; dot.style.display = 'none';
    state('Camera stopped'); $('hxTryStart').disabled = false;
    ['hxTryRecal', 'hxTryDot', 'hxTryStop'].forEach(function (id) { $(id).disabled = true; });
  });
})();
