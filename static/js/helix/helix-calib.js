/* Helix calibration UI shared by lesson pages and the "Try Helix" page.
   1. positioning: live mirrored preview + distance / centring / head-pose / light / glare checklist
   2. calibration, one of
        dots:   tap or click each dot and hold your gaze while it fills (keyboard: Tab + Space)
        follow: follow one moving dot with your eyes for ~9 s (smooth pursuit), then 3 anchor dots
   3. validation: look at 5 fresh dots; error reported in px and degrees, AOI resolution chosen
   A progress bar spans all three steps; time-to-calibrate is measured and returned in
   score.calibMs (first calibration dot to end of validation) and score.totalMs (incl. positioning).
   run(engine, opts) -> Promise<{action: 'go'|'retry'|'passive'|'cancel', score, ...}> */
(function () {
  'use strict';
  var Core = window.HelixCore, Model = window.HelixModel;
  var FULL = [[10, 10], [50, 10], [90, 10], [10, 50], [50, 50], [90, 50], [10, 90], [50, 90], [90, 90]];
  var QUICK = [[12, 14], [88, 14], [50, 50], [12, 86], [88, 86]];
  var VAL = [[50, 50], [20, 22], [80, 22], [20, 78], [80, 78]];
  // 0.9 s hold: 250 ms to land on the dot + ~0.65 s of samples (about 18 frames at 30 fps)
  var HOLD_MS = 900, SETTLE_MS = 250, MIN_FRAMES = 8, MAX_HOLD_MS = 4000;
  var PURSUIT_S = 9, ANCHORS = [[50, 50], [12, 14], [88, 86]];
  var CHEER = ['Nice.', 'Good.', 'Great \u2014 keep going.', 'Halfway there.', 'Lovely.', 'Nearly done.', 'Almost there.', 'Last one!'];

  function el(tag, attrs, html) { var n = document.createElement(tag); Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); }); if (html != null) n.innerHTML = html; return n; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function overlay() {
    var ov = el('div', { id: 'helixCalib', 'class': 'helix-calib', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'hxCalTitle' });
    ov.innerHTML = '<div class="hx-cal-help" aria-live="polite"></div>';
    document.body.appendChild(ov);
    return ov;
  }
  /* overall progress across positioning (0-15%), calibration (15-70%) and the check (70-100%) */
  function progress(ov, frac, label) {
    var b = ov.querySelector('.hx-cal-progress');
    if (!b) { b = el('div', { 'class': 'hx-cal-progress', role: 'progressbar', 'aria-valuemin': '0', 'aria-valuemax': '100', 'aria-label': 'Calibration progress' }, '<span></span>'); ov.insertBefore(b, ov.firstChild); }
    var v = Math.round(Math.max(0, Math.min(1, frac)) * 100);
    b.setAttribute('aria-valuenow', String(v)); if (label) b.setAttribute('aria-valuetext', label);
    b.firstChild.style.width = v + '%';
  }
  function help(ov, html, cls) { var h = ov.querySelector('.hx-cal-help'); h.className = 'hx-cal-help' + (cls ? ' ' + cls : ''); h.innerHTML = html; return h; }

  /* ---------------- step 1: positioning */
  function position(ov, engine, opts) {
    if (engine.kind !== 'mediapipe' || !engine.video) { if (engine.showPreview) engine.showPreview(true); return Promise.resolve('ok'); }
    return new Promise(function (resolve) {
      var h = help(ov, '<h2 id="hxCalTitle" class="h5">Get into position <span class="hx-cal-step">step 1 of 3</span></h2>' +
        '<div class="hx-pos"><div class="hx-pos-video"><svg class="hx-pos-oval" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><ellipse cx="50" cy="48" rx="23" ry="33"/></svg></div>' +
        '<ul class="hx-pos-checks" id="hxPosChecks"></ul></div>' +
        '<p class="small mb-2" id="hxPosHint">' + (engine.mobile ? 'Hold the phone upright at about a forearm\u2019s length, camera at eye level.' : 'Sit about an arm\u2019s length from the screen, camera at eye level.') + '</p>' +
        (canFollow(engine) ? '<fieldset class="hx-method mb-2"><legend class="small mb-1">How would you like to calibrate?</legend>' +
          '<label class="hx-method-opt"><input type="radio" name="hxMethod" value="follow"' + (opts.method === 'follow' ? ' checked' : '') + '> <span><strong>Follow a moving dot</strong><small>about 15 s, no clicking</small></span></label>' +
          '<label class="hx-method-opt"><input type="radio" name="hxMethod" value="dots"' + (opts.method !== 'follow' ? ' checked' : '') + '> <span><strong>Tap ' + (opts.quick ? 5 : 9) + ' dots</strong><small>about 15 s, most reliable</small></span></label></fieldset>' : '') +
        '<div class="d-flex flex-wrap gap-2 justify-content-center"><button type="button" class="btn btn-brand" id="hxPosGo" disabled>Start calibration</button>' +
        '<button type="button" class="btn btn-outline-light" id="hxPosSkip" hidden>Continue anyway</button>' +
        '<button type="button" class="btn btn-link text-reset" id="hxPosCancel">Cancel</button></div>', 'is-pos');
      var box = h.querySelector('.hx-pos-video');
      engine.video.classList.add('hx-video-mirror'); box.insertBefore(engine.video, box.firstChild);
      var go = h.querySelector('#hxPosGo'), skip = h.querySelector('#hxPosSkip'), list = h.querySelector('#hxPosChecks');
      var okSince = 0, t0 = Date.now(), done = false, askedExposure = false;
      var timer = setInterval(function () {
        var g = engine.guidance();
        list.innerHTML = g.checks.map(function (c) {
          return '<li class="' + (c.ok ? 'ok' : 'bad') + '"><i class="bi ' + (c.ok ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill') + '" aria-hidden="true"></i> ' + esc(c.label) + (c.ok || !c.hint ? '' : ' <span class="hx-pos-hint">' + esc(c.hint) + '</span>') + '</li>';
        }).join('');
        box.classList.toggle('good', g.ok);
        if (g.ok) { if (!okSince) okSince = Date.now(); } else okSince = 0;
        var wasDisabled = go.disabled;
        go.disabled = !(okSince && Date.now() - okSince > 700);
        if (wasDisabled && !go.disabled) go.textContent = 'Looks good \u2014 start calibration';
        var dark = g.checks.some(function (c) { return c.key === 'light' && !c.ok; });
        if (dark && !askedExposure && engine.exposureHint) { askedExposure = true; engine.exposureHint(); }
        var passed = g.checks.filter(function (c) { return c.ok; }).length;
        progress(ov, 0.15 * passed / Math.max(1, g.checks.length), 'Getting into position');
        if (Date.now() - t0 > 5000) skip.hidden = false;
      }, 250);
      function finish(v) {
        if (done) return; done = true; clearInterval(timer);
        var m = h.querySelector('input[name="hxMethod"]:checked'); if (m) opts.method = m.value;
        resolve(v);
      }
      go.addEventListener('click', function () { finish('ok'); });
      skip.addEventListener('click', function () { finish('ok'); });
      h.querySelector('#hxPosCancel').addEventListener('click', function () { finish('cancel'); });
      ov._esc = function () { finish('cancel'); };
    });
  }

  /* ---------------- step 2: calibration dots */
  function canFollow(engine) { return engine.kind === 'mediapipe' && typeof engine.beginPursuit === 'function'; }

  function calibrateDots(ov, engine, points, stepLabel, p0, p1) {
    p0 = p0 == null ? 0.15 : p0; p1 = p1 == null ? 0.7 : p1;
    return new Promise(function (resolve) {
      var touch = engine.mobile || (window.matchMedia && matchMedia('(pointer: coarse)').matches);
      help(ov, '<h2 id="hxCalTitle" class="h5">' + (stepLabel || 'Calibrate') + ' <span class="hx-cal-step">step 2 of 3</span></h2>' +
        '<p class="mb-1">' + (touch ? '<strong>Tap each dot</strong>' : '<strong>Click each dot</strong>') + ' and keep looking at its centre until it turns gold (under a second). Move your eyes, not your head.</p>' +
        '<p class="small mb-0"><span id="hxCalCount">0</span> / ' + points.length + ' dots · <span id="hxCheer" class="hx-cheer"></span> <span id="hxFaceState" class="hx-face-state">face tracked</span> · Keyboard: Tab + Space · <button type="button" class="btn btn-link btn-sm p-0 text-reset" id="hxCalCancel">Cancel (Esc)</button></p>');
      progress(ov, p0, 'Calibrating, 0 of ' + points.length + ' dots');
      if (engine.park) engine.park();
      if (engine.showPreview) engine.showPreview(true);
      var done = 0, busy = false, faceOk = true;
      var faceSpan = ov.querySelector('#hxFaceState');
      var faceT = setInterval(function () {
        var st = engine.stats(); faceOk = engine.kind !== 'mediapipe' || !!engine.lastFeat;
        faceSpan.textContent = faceOk ? 'face tracked' : 'face not found'; faceSpan.classList.toggle('bad', !faceOk);
        void st;
      }, 300);
      var btns = points.map(function (p, i) {
        var b = el('button', { type: 'button', 'class': 'hx-cal-pt' + (touch ? ' touch' : ''), style: 'left:' + p[0] + '%;top:' + p[1] + '%', 'aria-label': 'Calibration dot ' + (i + 1) + ' of ' + points.length });
        b.innerHTML = '<span class="hx-ring" style="--p:0"></span>';
        ov.appendChild(b);
        b.addEventListener('click', function () {
          if (busy || b.classList.contains('done')) return;
          busy = true; b.classList.add('active');
          var r = b.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
          engine.beginSample(x, y, SETTLE_MS);
          var ring = b.querySelector('.hx-ring'), t0 = Date.now();
          // hold for HOLD_MS, and longer on slow devices until enough frames were captured (max 4 s)
          var enough = function () { return engine.sampleCount() >= MIN_FRAMES || Date.now() - t0 > MAX_HOLD_MS; };
          var anim = setInterval(function () {
            var tp = (Date.now() - t0) / HOLD_MS, fp = engine.sampleCount() / MIN_FRAMES;
            ring.style.setProperty('--p', String(Math.min(1, Math.min(tp, Math.max(fp, tp * 0.9)))));
            if (tp >= 1 && enough()) { clearInterval(anim); finishDot(); }
          }, 50);
          function finishDot() {
            var n = engine.endSample();
            b.classList.remove('active');
            if (engine.kind === 'mediapipe' && n < 3) {   // eyes closed / face lost: ask again
              ring.style.setProperty('--p', '0'); busy = false;
              faceSpan.textContent = 'face not found \u2014 try that dot again'; faceSpan.classList.add('bad');
              return;
            }
            b.classList.add('done'); b.setAttribute('aria-label', b.getAttribute('aria-label') + ' \u2014 done');
            done++; ov.querySelector('#hxCalCount').textContent = String(done); busy = false;
            progress(ov, p0 + (p1 - p0) * done / points.length, 'Calibrating, ' + done + ' of ' + points.length + ' dots');
            var left = points.length - done, ch = ov.querySelector('#hxCheer');
            if (ch) ch.textContent = left === 0 ? 'All done!' : left === 1 ? CHEER[7] : done === Math.ceil(points.length / 2) ? CHEER[3] : CHEER[(done - 1) % 3];
            var next = btns.filter(function (x) { return !x.classList.contains('done'); })[0];
            btns.forEach(function (x) { x.classList.remove('next'); });
            if (next) { next.classList.add('next'); next.focus({ preventScroll: true }); }
            else { clearInterval(faceT); resolve('ok'); }
          }
        });
        return b;
      });
      btns[0].classList.add('next'); btns[0].focus({ preventScroll: true });
      ov.querySelector('#hxCalCancel').addEventListener('click', function () { clearInterval(faceT); resolve('cancel'); });
      ov._esc = function () { clearInterval(faceT); resolve('cancel'); };
    });
  }

  /* ---------------- step 2 (alternative): follow the moving dot */
  function pursuitPos(s, w, h) {
    // the path the accuracy proxy was measured on (tools/helix_eval/warp/gen.py): a Lissajous
    // figure, peak speed ~18 deg/s at 60 cm, well inside comfortable smooth-pursuit range
    return { x: w / 2 + 0.42 * w * Math.sin(2 * Math.PI * s / 4.5), y: h / 2 + 0.40 * h * Math.sin(2 * Math.PI * s / 3.0 + 0.6) };
  }
  function calibratePursuit(ov, engine) {
    return new Promise(function (resolve) {
      help(ov, '<h2 id="hxCalTitle" class="h5">Follow the dot <span class="hx-cal-step">step 2 of 3</span></h2>' +
        '<p class="mb-1">Keep your eyes on the gold dot as it glides around. Keep your head still \u2014 just your eyes.</p>' +
        '<p class="small mb-0"><span id="hxCheer" class="hx-cheer">Get ready\u2026</span> <span id="hxFaceState" class="hx-face-state">face tracked</span> · <button type="button" class="btn btn-link btn-sm p-0 text-reset" id="hxCalCancel">Cancel (Esc)</button></p>');
      if (engine.park) engine.park();
      if (engine.showPreview) engine.showPreview(true);
      var dot = el('div', { 'class': 'hx-pursuit-dot', 'aria-hidden': 'true' }); ov.appendChild(dot);
      var w = innerWidth, h = innerHeight, start = pursuitPos(0, w, h), stopped = false, path = null, raf = 0;
      var cheer = ov.querySelector('#hxCheer'), face = ov.querySelector('#hxFaceState'), lost = 0, frames = 0;
      dot.style.left = start.x + 'px'; dot.style.top = start.y + 'px';
      var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (reduce) cheer.textContent = 'The dot moves slowly and smoothly; look away any time to stop (Esc).';
      // 1.2 s to find the dot, then it moves; the engine pairs each frame with where the dot was
      // a moment earlier (the eye trails a moving target by ~100-200 ms, fitted per person)
      var lead = setTimeout(function () {
        path = engine.beginPursuit(); var t0 = performance.now(), w0 = Date.now();
        var step = function () {
          if (stopped) return;
          var s = (performance.now() - t0) / 1000, p = pursuitPos(s, w, h);
          dot.style.left = p.x + 'px'; dot.style.top = p.y + 'px';
          path.push({ t: w0 + s * 1000, x: p.x, y: p.y });
          var frac = Math.min(1, s / PURSUIT_S);
          progress(ov, 0.15 + 0.4 * frac, 'Following the dot');
          if (!reduce) cheer.textContent = frac < 0.35 ? 'Great, stay with it\u2026' : frac < 0.7 ? 'You\u2019re doing well\u2026' : 'Nearly there\u2026';
          frames++; if (!engine.lastFeat) lost++;
          face.textContent = engine.lastFeat ? 'face tracked' : 'face not found'; face.classList.toggle('bad', !engine.lastFeat);
          if (s >= PURSUIT_S) { finish(); return; }
          raf = requestAnimationFrame(step);
        };
        raf = requestAnimationFrame(step);
      }, 1200);
      function cleanup() { stopped = true; clearTimeout(lead); cancelAnimationFrame(raf); dot.remove(); }
      function finish() {
        cleanup();
        var fit = engine.endPursuit();
        // too few usable frames (face lost, eyes closed) -> fall back to the dot method
        resolve(fit && fit.samples >= 40 && lost / Math.max(1, frames) < 0.4 ? { ok: true, fit: fit } : { ok: false, fit: fit });
      }
      var cancel = function () { cleanup(); if (path) engine.endPursuit(); resolve('cancel'); };
      ov.querySelector('#hxCalCancel').addEventListener('click', cancel);
      ov._esc = cancel;
    });
  }

  /* ---------------- step 3: validation */
  function validate(ov, engine, opts) {
    ov.querySelectorAll('.hx-cal-pt').forEach(function (b) { b.remove(); });
    if (engine.showPreview) engine.showPreview(false);
    help(ov, '<h2 id="hxCalTitle" class="h5">Quick check <span class="hx-cal-step">step 3 of 3</span></h2><p class="mb-0">Just <strong>look</strong> at each dot as it appears \u2014 no clicking. About 8 seconds.</p>');
    progress(ov, 0.7, 'Checking accuracy');
    var nDone = 0;
    var target = el('div', { 'class': 'hx-val-pt', 'aria-hidden': 'true' }); ov.appendChild(target);
    var w = innerWidth, h = innerHeight, results = [], sink = null, filt = new Core.GazeFilter({ bounds: { w: w, h: h } });
    var dists = [];
    var lis = engine.on(function (ev) {
      if (!sink || !ev.pred) return;
      var f = filt.push(ev.pred.x, ev.pred.y);
      if (f.ok) sink.push({ x: f.x, y: f.y, raw: ev.pred });
      if (ev.feat && ev.feat.distanceCm) dists.push(ev.feat.distanceCm);
    });
    return VAL.reduce(function (p, pt) {
      return p.then(function () {
        var x = pt[0] / 100 * w, y = pt[1] / 100 * h, samples = [];
        target.style.left = x + 'px'; target.style.top = y + 'px';
        target.classList.remove('pulse'); void target.offsetWidth; target.classList.add('pulse');
        return wait(550).then(function () {
          sink = samples;
          // 1.1 s window, extended on slow devices until 6 estimates arrived (max 3 s)
          return new Promise(function (res) { var t0 = Date.now(); var iv = setInterval(function () { var dt = Date.now() - t0; if ((dt >= 1100 && samples.length >= 6) || dt >= 3000) { clearInterval(iv); res(); } }, 50); });
        }).then(function () { sink = null; results.push({ x: x, y: y, samples: samples }); nDone++; progress(ov, 0.7 + 0.3 * nDone / VAL.length, 'Checking accuracy, ' + nDone + ' of ' + VAL.length); });
      });
    }, Promise.resolve()).then(function () {
      engine.off(lis);
      target.remove();
      var score = Core.scoreValidation(results, { w: w, h: h });
      dists.sort(function (a, b) { return a - b; });
      var dist = dists.length ? dists[dists.length >> 1] : null;
      score.distanceCm = dist ? Math.round(dist) : null;
      score.errorDeg = score.valid ? Model.angularError(score.errorPx, dist) : null;
      if (score.errorDeg != null) score.errorDeg = Math.round(score.errorDeg * 10) / 10;
      score.resolution = score.valid ? Model.aoiResolution(score.errorPx, opts.metrics) : 'heading';
      score.engine = engine.kind; score.delegate = engine.delegate; score.points = results.length;
      return { score: score, results: results };
    });
  }

  var RES_TEXT = {
    line: 'Precise enough for <strong>line-level</strong> areas (unusual for a webcam \u2014 nice setup).',
    paragraph: 'Precise enough for <strong>paragraph-level</strong> areas of interest.',
    heading: 'Helix will track <strong>heading-level</strong> sections (finer areas need a lower error).'
  };

  function result(ov, engine, v, opts, attempt) {
    return new Promise(function (resolve) {
      var s = v.score, min = opts.minAccuracy || 45, ok = s.score >= min;
      var marks = v.results.map(function (r) {
        if (!r.samples.length) return '<span class="hx-val-target" style="left:' + r.x + 'px;top:' + r.y + 'px"></span>';
        var cx = r.samples.reduce(function (a, q) { return a + q.x; }, 0) / r.samples.length, cy = r.samples.reduce(function (a, q) { return a + q.y; }, 0) / r.samples.length;
        return '<span class="hx-val-target" style="left:' + r.x + 'px;top:' + r.y + 'px"></span><span class="hx-val-line" style="left:' + r.x + 'px;top:' + r.y + 'px;width:' + Math.hypot(cx - r.x, cy - r.y) + 'px;transform:rotate(' + Math.atan2(cy - r.y, cx - r.x) + 'rad)"></span><span class="hx-val-est" style="left:' + cx + 'px;top:' + cy + 'px"></span>';
      }).join('');
      ov.insertAdjacentHTML('beforeend', marks);
      var err = s.valid ? '<p class="mb-1">Median error <strong>' + s.errorPx + ' px</strong>' + (s.errorDeg != null ? ' \u2248 <strong>' + s.errorDeg + '\u00b0</strong> of visual angle' + (s.distanceCm ? ' at ~' + s.distanceCm + ' cm' : '') : '') + '; spread ' + s.precisionPx + ' px.</p>' +
        '<p class="small mb-2 opacity-75">Rings = targets, dots = Helix\u2019s estimate. Degrees assume 96 CSS px per inch and the camera\u2019s distance estimate.</p>' : '';
      var tips = '<ul class="small text-start mb-2"><li>Light your face from the front; avoid a bright window behind you.</li><li>Keep the camera at eye level; move your eyes rather than your head.</li><li>Clean the camera lens; tilt glasses slightly if they reflect.</li></ul>';
      help(ov,
        (s.valid ? '<h2 class="h5">' + (ok ? 'You\u2019re all set! ' : '') + 'Accuracy: ' + s.score + '% <span class="hx-acc hx-acc-' + s.band + '">' + s.band + '</span></h2>' + err +
          (s.calibMs ? '<p class="small mb-2 opacity-75">Calibrated in ' + Math.round(s.calibMs / 1000) + ' s (' + (s.calibMode === 'follow' ? 'follow the dot' : s.calibMode === 'follow+dots' ? 'follow the dot, then dots' : 'dots') + ').</p>' : '')
                 : '<h2 class="h5">No gaze estimates received <span class="hx-acc hx-acc-poor">poor</span></h2><p class="mb-2">Helix could not see your eyes during the check. Check the lighting and that your face is in view.</p>') +
        (s.valid ? '<p class="mb-2">' + RES_TEXT[s.resolution] + '</p>' : '') +
        (ok ? '' : '<p class="mb-2"><strong>Not quite there yet (below ' + min + '%).</strong> That\u2019s common on the first try \u2014 one of these usually fixes it:</p>' + tips) +
        '<div class="d-flex flex-wrap gap-2 justify-content-center">' +
        (ok ? '<button type="button" class="btn btn-brand" id="hxGo">' + esc(opts.goLabel || 'Start reading') + '</button>' : '') +
        '<button type="button" class="btn ' + (ok ? 'btn-outline-light' : 'btn-brand') + '" id="hxRetry">Recalibrate</button>' +
        (!ok && attempt >= 2 && opts.allowPassive ? '<button type="button" class="btn btn-outline-light" id="hxToPassive">Use reading signal instead</button>' : '') +
        (!ok ? '<button type="button" class="btn btn-outline-light" id="hxGoAnyway">Continue anyway</button>' : '') + '</div>', 'is-result');
      var bind = function (id, action) { var b = ov.querySelector('#' + id); if (b) b.addEventListener('click', function () { resolve(action); }); };
      bind('hxGo', 'go'); bind('hxGoAnyway', 'go'); bind('hxRetry', 'retry'); bind('hxToPassive', 'passive');
      ov._esc = function () { resolve('cancel'); };
      var first = ov.querySelector('.hx-cal-help .btn'); if (first) first.focus();
    });
  }

  function run(engine, opts) {
    opts = opts || {};
    var attempt = 0;
    var ov = overlay();
    var esck = function (e) { if (e.key === 'Escape' && ov._esc) ov._esc(); };
    document.addEventListener('keydown', esck);
    var close = function (out) { document.removeEventListener('keydown', esck); if (engine.showPreview) engine.showPreview(false); ov.remove(); return out; };
    var points = opts.quick ? QUICK : FULL;
    var tStart = Date.now();
    var once = function () {
      attempt++; if (attempt > 1) tStart = Date.now();
      ov.querySelectorAll('.hx-val-target,.hx-val-est,.hx-val-line').forEach(function (n) { n.remove(); });
      return (opts.skipPositioning || attempt > 1 ? Promise.resolve('ok') : position(ov, engine, opts)).then(function (r) {
        if (r === 'cancel') return { action: 'cancel' };
        engine.resetCalibration();
        var tCal = Date.now(), mode = canFollow(engine) && opts.method === 'follow' ? 'follow' : 'dots';
        var step2 = mode === 'follow'
          ? calibratePursuit(ov, engine).then(function (pr) {
              if (pr === 'cancel') return 'cancel';
              ov.querySelectorAll('.hx-cal-pt').forEach(function (b) { b.remove(); });
              // a few fixation dots anchor the absolute offset; if the follow step lost the face,
              // fall back to the full dot set instead of failing
              if (!pr.ok) { mode = 'follow+dots'; return calibrateDots(ov, engine, points, 'Let\u2019s use dots instead', 0.55, 0.7); }
              return calibrateDots(ov, engine, ANCHORS, 'Three quick dots', 0.55, 0.7).then(function (x) { lagMs = pr.fit && pr.fit.lagMs; return x; });
            })
          : calibrateDots(ov, engine, points);
        var lagMs = null;
        return step2.then(function (r2) {
          if (r2 === 'cancel') return { action: 'cancel' };
          engine.fit();
          return validate(ov, engine, opts).then(function (v) {
            v.score.calibMs = Date.now() - tCal; v.score.totalMs = Date.now() - tStart;
            v.score.calibMode = mode; if (lagMs != null) v.score.pursuitLagMs = lagMs;
            if (opts.onValidated) opts.onValidated(v.score, attempt);
            return result(ov, engine, v, opts, attempt).then(function (action) {
              if (action === 'retry') return once();
              return { action: action, score: v.score, attempt: attempt };
            });
          });
        });
      });
    };
    return once().then(close, function (e) { close(); throw e; });
  }

  window.HelixCalib = { run: run, FULL: FULL, QUICK: QUICK, VAL: VAL, ANCHORS: ANCHORS, pursuitPos: pursuitPos, PURSUIT_S: PURSUIT_S };
})();
