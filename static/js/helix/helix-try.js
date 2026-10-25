/* Try Helix: local-only gaze playground (no uploads). Also the end-to-end test harness hook:
   window.HelixTry exposes live state for tools/helix_e2e.py and tools/helix_mp_e2e.py. */
(function () {
  'use strict';
  var E = window.HelixEngine, Calib = window.HelixCalib, Core = window.HelixCore, Model = window.HelixModel, CFG = window.HELIX_ENGINE || {};
  var $ = function (id) { return document.getElementById(id); };
  var T = window.HelixTry = { engine: null, preds: 0, frames: 0, lastPred: null, score: null, history: [], trailPts: [], error: null, targetTest: null };
  var showDot = true, filt = null, drift = new Model.DriftTracker({ window: 7 }), playBlocked = false, targetRunning = false;
  var dot = $('helixGazeDot'), trail = $('hxTryTrail'), tiles = Array.prototype.slice.call(document.querySelectorAll('.hx-try-tile'));

  var qsInit = new URLSearchParams(location.search);
  if ($('hxTryHiRes')) {
    $('hxTryHiRes').checked = qsInit.get('crop') !== '0' && qsInit.get('hires') !== '0';
  }
  if ($('hxTryQuick') && qsInit.get('quick') === '1') {
    $('hxTryQuick').checked = true;
  }

  function state(t) { $('hxTryState').textContent = t; }
  function hud() {
    if (!T.engine) return;
    var s = T.engine.stats(), rows = [
      ['Engine', s.engine + (T.engine.fallbackReason ? ' (MediaPipe failed: ' + T.engine.fallbackReason + ')' : '')],
      ['Delegate', s.delegate || '—'], ['Frame rate', (s.fps || 0).toFixed(1) + ' fps' + (s.targetFps ? ' (target ' + s.targetFps + ')' : '')],
      ['Inference', s.inferMs != null ? s.inferMs + ' ms/frame' : '—'], ['Face found', Math.round((s.faceRate || 0) * 100) + '% of frames'],
      ['Distance', s.distanceCm ? '~' + s.distanceCm + ' cm' : '—'], ['Head yaw / pitch', s.yawDeg != null ? s.yawDeg + '° / ' + s.pitchDeg + '°' : '—'],
      ['Training samples', (s.samples || 0) + ' calibration' + (s.implicit != null ? ' + ' + s.implicit + ' implicit' : '')],
      ['Model', s.lambda != null ? 'ridge ' + (s.lambdaX != null && s.lambdaY != null && s.lambdaX !== s.lambdaY ? 'λx=' + s.lambdaX + ' λy=' + s.lambdaY : 'λ=' + s.lambda) + (s.lambdaSel === 'cv' ? ' (grouped CV)' : ' (GCV)') + (s.modelCrop ? ' + eye-crop features' : '') + ', fit RMS ' + s.fitRmsPx + ' px' : '—'], ['Orientation', s.orientation || '—'],
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
  var activeTileIdx = -1, candTileIdx = -1, candTileSince = 0;
  function onFrame(ev) {
    T.frames++;
    if (!ev.pred) return;
    var prev = T.lastPred;
    var f = filt.push(ev.pred.x, ev.pred.y, ev.t);
    if (!f.ok) return;
    var now = ev.t || Date.now();
    var hitIdx = -1, hitRect = null;
    for (var i = 0; i < tiles.length; i++) {
      var r = tiles[i].getBoundingClientRect();
      var pad = (i === activeTileIdx) ? 16 : 6;
      if (f.x >= r.left - pad && f.x <= r.right + pad && f.y >= r.top - pad && f.y <= r.bottom + pad) {
        hitIdx = i; hitRect = r; break;
      }
    }
    if (hitIdx === activeTileIdx) {
      candTileIdx = hitIdx; candTileSince = now;
    } else {
      if (hitIdx !== candTileIdx) { candTileIdx = hitIdx; candTileSince = now; }
      if (now - candTileSince >= (f.jumped ? 40 : 120)) activeTileIdx = hitIdx;
    }
    var dispX = f.x, dispY = f.y;
    var step = prev ? Math.hypot(f.x - prev.x, f.y - prev.y) : 0;
    if (activeTileIdx >= 0 && tiles[activeTileIdx] && step < 36) {
      var ar = hitIdx === activeTileIdx && hitRect ? hitRect : tiles[activeTileIdx].getBoundingClientRect();
      var cx = ar.left + ar.width / 2, cy = ar.top + ar.height / 2;
      dispX = f.x + 0.22 * (cx - f.x);
      dispY = f.y + 0.22 * (cy - f.y);
    }
    T.preds++; T.lastPred = { x: dispX, y: dispY, rawX: f.x, rawY: f.y, tile: activeTileIdx, t: now };
    T.history.push({ x: Math.round(dispX), y: Math.round(dispY), t: now }); if (T.history.length > 600) T.history.shift();
    T.trailPts.push({ x: dispX, y: dispY }); if (T.trailPts.length > 24) T.trailPts.shift();
    if (showDot) { dot.style.display = 'block'; dot.style.transform = 'translate(' + (dispX - 9) + 'px,' + (dispY - 9) + 'px)'; }
    drawTrail();
    tiles.forEach(function (t, idx) {
      t.classList.toggle('hot', idx === activeTileIdx);
    });
  }

  function showResult(s) {
    T.score = s;
    $('hxTryResult').innerHTML = s.valid
      ? '<p class="display-6 mb-0">' + s.errorPx + ' px</p><p class="mb-2">median error' + (s.errorDeg != null ? ' \u2248 <strong>' + s.errorDeg + '\u00b0</strong> visual angle' : '') + (s.distanceCm ? ' at ~' + s.distanceCm + ' cm' : '') + '</p>' +
        '<ul class="small mb-0"><li>Score ' + s.score + '% (' + s.band + ')</li><li>Spread (precision) ' + s.precisionPx + ' px</li><li>AOI resolution supported: <strong>' + s.resolution + '</strong></li><li>Engine: ' + s.engine + ' / ' + (s.delegate || '—') + '</li></ul>'
      : '<p class="mb-0">No gaze estimates during the check \u2014 the camera could not see your eyes.</p>';
  }

  function enableControls(on) {
    ['hxTryRecal', 'hxTryTargetBtn', 'hxTryDot', 'hxTryStop'].forEach(function (id) {
      var b = $(id); if (b) b.disabled = !on;
    });
  }

  function refreshSavedBtn() {
    var b = $('hxTryUseSaved');
    if (!b || !E || !E.getSessionCalibration) return;
    var saved = E.getSessionCalibration();
    b.hidden = !saved;
    if (saved && saved.score && saved.score.errorPx != null) {
      b.innerHTML = '<i class="bi bi-check2-circle" aria-hidden="true"></i> Use saved calibration (' + saved.score.errorPx + ' px)';
    }
  }
  refreshSavedBtn();

  function calibrate(quick) {
    var useQuick = quick != null ? quick : !!($('hxTryQuick') && $('hxTryQuick').checked);
    state('Calibrating\u2026');
    return Calib.run(T.engine, { quick: useQuick, skipPositioning: !!quick, minAccuracy: 0, goLabel: 'Start tracking', allowPassive: false, onValidated: showResult })
      .then(function (r) {
        refreshSavedBtn();
        if (r.action === 'cancel') { state(T.engine.ready() ? 'Tracking (calibration cancelled)' : 'Calibration cancelled'); return; }
        filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
        state('Tracking \u2014 look around the tiles');
      });
  }

  function start(useSaved) {
    useSaved = useSaved === true;
    if (playBlocked && T.engine && T.engine.resumePlayback) {
      playBlocked = false;
      $('hxTryStart').disabled = true;
      $('hxTryStart').innerHTML = '<i class="bi bi-camera-video" aria-hidden="true"></i> Start camera &amp; calibrate';
      T.engine.resumePlayback().then(function () {
        filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
        T.engine.on(onFrame);
        enableControls(true);
        if (useSaved && T.engine.loadSessionCalibration && T.engine.loadSessionCalibration()) {
          if (T.engine.calScore) showResult(T.engine.calScore);
          state('Tracking (restored saved calibration) \u2014 look around the tiles');
          return;
        }
        return calibrate(false);
      }).catch(function (err) {
        T.error = String(err && err.message || err);
        state('Could not resume: ' + T.error); $('hxTryStart').disabled = false;
      });
      return;
    }
    var qs = new URLSearchParams(location.search);
    var qc = qs.get('crop');
    var hiToggle = $('hxTryHiRes');
    var wantHi = qs.get('hires') === '0' ? false : (hiToggle ? hiToggle.checked : true);
    var cropMode = qc === '0' ? false : qc === '1' ? true : 'view';
    CFG.hiRes = wantHi;
    // Open camera synchronously inside the user tap/click gesture before awaiting MediaPipe WASM load
    if (E && E.prefetchCamera) {
      try { E.prefetchCamera(E.isMobile && E.isMobile()); } catch (e) {}
    }
    $('hxTryStart').disabled = true; state('Loading gaze engine\u2026');
    var prefer = $('hxTryEngine').value;
    var qd = qs.get('delegate');
    E.create(Object.assign({ prefer: prefer, delegate: qd === 'CPU' ? 'CPU' : null, crop: cropMode }, CFG)).then(function (engine) {
      T.engine = engine; engine.keepCrops = true; state('Waiting for camera permission\u2026');
      return engine.start();
    }).then(function (engine) {
      filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
      engine.on(onFrame);
      enableControls(true);
      if (useSaved && engine.loadSessionCalibration && engine.loadSessionCalibration()) {
        if (engine.calScore) showResult(engine.calScore);
        state('Tracking (restored saved calibration) \u2014 look around the tiles');
        return;
      }
      return calibrate(false);
    }).catch(function (err) {
      if (err && err.code === 'play_blocked' && T.engine && T.engine.resumePlayback) {
        playBlocked = true;
        state('Tap "Resume camera" to allow video playback');
        $('hxTryStart').textContent = 'Resume camera';
        $('hxTryStart').disabled = false;
        return;
      }
      T.error = String(err && err.message || err);
      state('Could not start: ' + T.error); $('hxTryStart').disabled = false;
    });
  }

  /* Interactive 5-tile live target verification test */
  function runTargetTest() {
    if (!T.engine || !T.engine.ready() || targetRunning) return;
    targetRunning = true;
    var btn = $('hxTryTargetBtn'), out = $('hxTryTargetOut');
    if (btn) btn.disabled = true;
    var seq = [4, 0, 2, 6, 8], idx = 0, hits = 0, dists = [];
    out.hidden = false;
    out.textContent = 'Live target test: look at each highlighted gold tile (1 of ' + seq.length + ')\u2026';
    state('Live target test running\u2026');

    function stepTile() {
      tiles.forEach(function (t) { t.classList.remove('target-cue'); var c = t.querySelector('.hx-tile-cue'); if (c) c.textContent = ''; });
      if (idx >= seq.length) {
        targetRunning = false;
        if (btn) btn.disabled = false;
        dists.sort(function (a, b) { return a - b; });
        var med = dists.length ? Math.round(dists[dists.length >> 1]) : null;
        T.targetTest = { hits: hits, total: seq.length, medianPx: med };
        out.innerHTML = '<strong>Live target test complete:</strong> hit <strong>' + hits + ' / ' + seq.length + ' tiles</strong>' +
          (med != null ? ' · median gaze offset <strong>' + med + ' px</strong> from tile centre.' : ' (no gaze samples received).');
        state('Tracking \u2014 target test ' + hits + '/' + seq.length + ' tiles');
        return;
      }
      var ti = seq[idx], tile = tiles[ti];
      tile.classList.add('target-cue');
      var cue = tile.querySelector('.hx-tile-cue');
      if (cue) cue.textContent = 'Look here';
      out.textContent = 'Look at tile ' + (ti + 1) + ' (' + (idx + 1) + ' of ' + seq.length + ')\u2026';
      var tStart = Date.now() + 450, tileSamples = [];
      var lis = T.engine.on(function (ev) {
        if (!ev.pred || Date.now() < tStart || !T.lastPred) return;
        tileSamples.push({ x: T.lastPred.x, y: T.lastPred.y });
      });
      setTimeout(function () {
        T.engine.off(lis);
        var r = tile.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        if (tileSamples.length) {
          var sx = 0, sy = 0, inside = 0;
          tileSamples.forEach(function (p) {
            sx += p.x; sy += p.y;
            if (p.x >= r.left - 22 && p.x <= r.right + 22 && p.y >= r.top - 22 && p.y <= r.bottom + 22) inside++;
          });
          var mx = sx / tileSamples.length, my = sy / tileSamples.length;
          dists.push(Math.hypot(mx - cx, my - cy));
          if (inside >= Math.max(1, Math.floor(tileSamples.length * 0.30)) || ( mx >= r.left - 28 && mx <= r.right + 28 && my >= r.top - 28 && my <= r.bottom + 28 )) hits++;
        }
        idx++;
        stepTile();
      }, 1800);
    }
    stepTile();
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

  if ($('hxTryHiRes')) {
    $('hxTryHiRes').addEventListener('change', function () {
      CFG.hiRes = this.checked;
      if (T.engine && T.engine.opts) {
        T.engine.opts.crop = this.checked ? 'view' : false;
        T.engine.cropDisabled = false;
      }
    });
  }

  $('hxTryStart').addEventListener('click', function () { start(false); });
  if ($('hxTryUseSaved')) {
    $('hxTryUseSaved').addEventListener('click', function () {
      if (T.engine) {
        if (T.engine.loadSessionCalibration && T.engine.loadSessionCalibration()) {
          if (T.engine.calScore) showResult(T.engine.calScore);
          filt = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } });
          state('Tracking (restored saved calibration) \u2014 look around the tiles');
        }
      } else {
        start(true);
      }
    });
  }
  $('hxTryRecal').addEventListener('click', function () { calibrate(false); });
  if ($('hxTryTargetBtn')) $('hxTryTargetBtn').addEventListener('click', runTargetTest);
  $('hxTryDot').addEventListener('click', function () {
    showDot = !showDot; this.setAttribute('aria-pressed', String(showDot)); this.textContent = showDot ? 'Hide gaze dot' : 'Show gaze dot';
    if (!showDot) dot.style.display = 'none'; drawTrail();
  });
  $('hxTryStop').addEventListener('click', function () {
    if (T.engine) T.engine.stop(); T.engine = null; dot.style.display = 'none';
    playBlocked = false; targetRunning = false;
    state('Camera stopped'); $('hxTryStart').disabled = false;
    enableControls(false);
  });
})();
