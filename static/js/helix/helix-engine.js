/* Helix gaze engines.
   MediaPipeEngine (primary): self-hosted MediaPipe Face Landmarker (WASM, GPU delegate with CPU
   fallback) -> HelixModel.eyeFeatures -> per-user GazeRegressor (one per screen orientation),
   trained from calibration plus implicit samples. Front camera, playsinline, frame-rate throttling.
   WebGazerEngine (fallback): used only if MediaPipe cannot load (no WASM, blocked files, old browser).
   Both expose the same interface so the calibration UI and runtime do not care which one runs. */
(function () {
  'use strict';
  var Model = window.HelixModel;

  function isMobile() {
    var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    return coarse && Math.min(screen.width, screen.height) < 820;
  }
  function orientationKey() { return window.innerWidth >= window.innerHeight ? 'landscape' : 'portrait'; }
  function nowMs() { return (window.performance && performance.now) ? performance.now() : Date.now(); }

  function cameraConstraints(mobile) {
    return {
      audio: false,
      video: {
        facingMode: 'user',                                  // front camera on phones/tablets
        width: { ideal: mobile ? 480 : 640 }, height: { ideal: mobile ? 640 : 480 },
        frameRate: { ideal: mobile ? 24 : 30, max: 30 }
      }
    };
  }
  function cameraError(err) {
    var n = String(err && (err.name || err.message) || err);
    if (/NotAllowed|Permission|denied|Security/i.test(n)) return new Error('camera permission was denied');
    if (/NotFound|DevicesNotFound|Overconstrained/i.test(n)) return new Error('no front camera was found');
    if (/NotReadable|TrackStart/i.test(n)) return new Error('the camera is in use by another app');
    return err instanceof Error ? err : new Error(n);
  }

  /* ----------------------------------------------------------------- MediaPipe */
  // Keep estimates within the viewport plus a small margin: a gaze far off-screen means
  // "not on the page", which consumers treat the same as a clamped edge value.
  function clampPred(p) {
    if (!p || typeof window === 'undefined') return p;
    var w = window.innerWidth || 1, h = window.innerHeight || 1, mx = 0.08 * w, my = 0.08 * h;
    p.offscreen = p.x < -mx || p.y < -my || p.x > w + mx || p.y > h + my;
    p.x = Math.max(-mx, Math.min(w + mx, p.x)); p.y = Math.max(-my, Math.min(h + my, p.y));
    return p;
  }

  function MediaPipeEngine(opts) {
    this.kind = 'mediapipe';
    this.opts = opts;
    this.mobile = opts.mobile == null ? isMobile() : opts.mobile;
    this.models = new Model.OrientationModels({});
    this.models.use(orientationKey());
    this.listeners = [];
    this.recent = [];              // last ~1 s of features, for implicit samples
    this.collect = null;           // active calibration collection
    this.maxFps = this.mobile ? 15 : 30; this.minFps = 6; this.fps = this.maxFps;
    this.inferEma = 0; this.frames = 0; this.faceFrames = 0; this.fpsWin = [];
    this.paused = false; this.running = false; this.lastFeat = null; this.delegate = null;
    this.brightness = null;
  }
  MediaPipeEngine.prototype.on = function (fn) { this.listeners.push(fn); return fn; };
  MediaPipeEngine.prototype.off = function (fn) { this.listeners = this.listeners.filter(function (f) { return f !== fn; }); };
  MediaPipeEngine.prototype._emit = function (ev) { this.listeners.forEach(function (fn) { try { fn(ev); } catch (e) { if (window.console) console.error(e); } }); };

  MediaPipeEngine.prototype.load = function () {
    var self = this, o = this.opts;
    return import(o.bundleUrl).then(function (vision) {
      self.vision = vision;
      return vision.FilesetResolver.forVisionTasks(o.wasmBase);
    }).then(function (fileset) {
      var make = function (delegate) {
        return self.vision.FaceLandmarker.createFromOptions(fileset, {
          baseOptions: { modelAssetPath: o.modelUrl, delegate: delegate },
          runningMode: 'VIDEO', numFaces: 1, minFaceDetectionConfidence: 0.5, minTrackingConfidence: 0.5,
          outputFacialTransformationMatrixes: true, outputFaceBlendshapes: true
        }).then(function (lm) { self.delegate = delegate; return lm; });
      };
      var order = o.delegate === 'CPU' ? ['CPU'] : ['GPU', 'CPU'];   // GPU (WebGL) first, CPU (WASM) fallback
      return order.reduce(function (p, d) { return p.catch(function () { return make(d); }); }, Promise.reject(new Error('start')));
    }).then(function (lm) { self.landmarker = lm; return self; });
  };

  MediaPipeEngine.prototype.start = function () {
    var self = this;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return Promise.reject(new Error('this browser cannot open the camera here (HTTPS is required)'));
    var v = this.video = document.createElement('video');
    v.setAttribute('playsinline', ''); v.setAttribute('webkit-playsinline', ''); v.muted = true; v.autoplay = true;
    v.className = 'hx-video';
    // the video must stay attached and "visible" or browsers stop delivering frames (iOS pauses it)
    var holder = document.getElementById('hxVideoHolder');
    if (!holder) { holder = document.createElement('div'); holder.id = 'hxVideoHolder'; holder.className = 'hx-video-holder'; holder.setAttribute('aria-hidden', 'true'); document.body.appendChild(holder); }
    holder.appendChild(v); this.holder = holder;
    return navigator.mediaDevices.getUserMedia(cameraConstraints(this.mobile)).catch(function (e) {
      // some devices reject the ideal size/frame rate: retry with the bare front camera
      if (/Overconstrained/i.test(String(e && e.name))) return navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'user' } });
      throw e;
    }).then(function (stream) {
      self.stream = stream; v.srcObject = stream;
      return v.play().catch(function () {});
    }).then(function () {
      return new Promise(function (res) { if (v.videoWidth) res(); else v.addEventListener('loadedmetadata', function () { res(); }, { once: true }); });
    }).then(function () {
      self.running = true; self._loop(); self._watchBattery(); return self;
    }).catch(function (e) { throw cameraError(e); });
  };

  MediaPipeEngine.prototype._watchBattery = function () {
    var self = this;
    if (!navigator.getBattery) return;
    navigator.getBattery().then(function (b) {
      var upd = function () { self.maxFps = (!b.charging && b.level < 0.25) ? 10 : (self.mobile ? 15 : 30); if (self.fps > self.maxFps) self.fps = self.maxFps; };
      upd(); b.addEventListener('levelchange', upd); b.addEventListener('chargingchange', upd);
    }).catch(function () {});
  };

  MediaPipeEngine.prototype.park = function () { if (this.video && this.holder && this.video.parentNode !== this.holder) this.holder.appendChild(this.video); };
  MediaPipeEngine.prototype._loop = function () {
    var self = this, v = this.video, last = 0, pending = false;
    var schedule = function () {
      if (!self.running || pending) return;
      pending = true;
      if (v.requestVideoFrameCallback) v.requestVideoFrameCallback(step); else requestAnimationFrame(step);
    };
    // watchdog: if frame callbacks stall (element moved, tab throttled), keep the loop alive
    clearInterval(this._wd);
    this._wd = setInterval(function () { if (self.running && Date.now() - self._lastStep > 600) { pending = false; step(); } }, 300);
    var step = function () {
      pending = false; self._lastStep = Date.now();
      if (!self.running) return;
      var t = nowMs();
      if (self.paused || document.hidden || t - last < 1000 / self.fps - 2) { schedule(); return; }
      last = t;
      self._process(t);
      schedule();
    };
    schedule();
  };

  MediaPipeEngine.prototype._process = function (t) {
    var res, v = this.video;
    var t0 = nowMs();
    try { res = this.landmarker.detectForVideo(v, t); } catch (e) { return; }
    var infer = nowMs() - t0;
    this.inferEma = this.inferEma ? this.inferEma * 0.9 + infer * 0.1 : infer;
    // thermal/battery friendly: frame budget adapts to how long inference takes on this device
    var budget = 1000 / this.fps;
    if (this.inferEma > budget * 0.7 && this.fps > this.minFps) this.fps = Math.max(this.minFps, this.fps - 2);
    else if (this.inferEma < budget * 0.35 && this.fps < this.maxFps) this.fps = Math.min(this.maxFps, this.fps + 1);
    this.frames++;
    this.fpsWin.push(t); while (this.fpsWin.length && t - this.fpsWin[0] > 2000) this.fpsWin.shift();
    if (this.frames % 15 === 1) this._measureBrightness();
    var lm = res && res.faceLandmarks && res.faceLandmarks[0];
    var feat = null;
    if (lm) {
      var mat = res.facialTransformationMatrixes && res.facialTransformationMatrixes[0];
      var bsc = res.faceBlendshapes && res.faceBlendshapes[0];
      feat = Model.eyeFeatures(lm, v.videoWidth, v.videoHeight, mat && mat.data, { blendshapes: bsc && bsc.categories, hfovDeg: this.opts.hfovDeg });
      if (feat) { this.faceFrames++; feat.landmarks = lm; }
    }
    this.lastFeat = feat;
    var wall = Date.now();
    if (feat && !feat.blink) {
      this.recent.push({ t: wall, feat: feat }); while (this.recent.length && wall - this.recent[0].t > 1200) this.recent.shift();
      if (this.collect && wall >= this.collect.from) this.collect.samples.push(feat);
    }
    var reg = this.models.current(), pred = null;
    if (feat && !feat.blink && reg && reg.model) pred = clampPred(reg.predict(feat.vec));
    this._emit({ t: wall, face: !!feat, blink: !!(feat && feat.blink), feat: feat, pred: pred, inferMs: infer });
  };

  MediaPipeEngine.prototype._measureBrightness = function () {
    try {
      var c = this._bc || (this._bc = document.createElement('canvas')); c.width = 32; c.height = 24;
      var g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(this.video, 0, 0, 32, 24);
      var d = g.getImageData(8, 4, 16, 16).data, s = 0;   // centre region, where the face usually is
      for (var i = 0; i < d.length; i += 4) s += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
      this.brightness = s / (d.length / 4);
    } catch (e) { this.brightness = null; }
  };

  /* calibration: collect features while the student looks at (x, y) */
  MediaPipeEngine.prototype.beginSample = function (x, y, settleMs) { this.collect = { x: x, y: y, from: Date.now() + (settleMs || 250), samples: [] }; };
  MediaPipeEngine.prototype.endSample = function () {
    var c = this.collect; this.collect = null;
    if (!c) return 0;
    var reg = this.models.current();
    c.samples.forEach(function (f) { reg.addCalibration(f.vec, c.x, c.y); });
    return c.samples.length;
  };
  MediaPipeEngine.prototype.sampleCount = function () { return this.collect ? this.collect.samples.length : 0; };
  MediaPipeEngine.prototype.resetCalibration = function () { var reg = this.models.current(); reg.cal = []; reg.model = null; };
  MediaPipeEngine.prototype.fit = function () { var m = this.models.current().fit(); return !!m; };
  MediaPipeEngine.prototype.ready = function () { return this.models.ready(); };

  /* implicit sample (click / tap / caret): features from ~80 ms before the event, when the eyes
     were on the target. Returns the prediction error measured *before* learning from it. */
  MediaPipeEngine.prototype.implicit = function (x, y, source, opts) {
    opts = opts || {};
    var reg = this.models.current();
    if (!reg || !reg.model || !this.recent.length) return null;
    var want = Date.now() - 80, best = null;
    this.recent.forEach(function (r) { if (!best || Math.abs(r.t - want) < Math.abs(best.t - want)) best = r; });
    if (!best || Math.abs(best.t - want) > 250) return null;
    var p = reg.predict(best.feat.vec), err = Math.hypot(p.x - x, p.y - y);
    var gate = (opts.gate || 0.35) * Math.hypot(window.innerWidth, window.innerHeight);
    if (err > gate) return { err: err, accepted: false };     // probably clicked without looking
    reg.addImplicit(best.feat.vec, x, y, source === 'caret' ? 0.5 : 1);
    var self = this;
    clearTimeout(this._refit); this._refit = setTimeout(function () { reg.fit(); }, 200);   // online adaptation
    return { err: err, accepted: true };
  };

  MediaPipeEngine.prototype.setOrientation = function (key) { this.models.use(key || orientationKey()); return this.models.ready(); };
  MediaPipeEngine.prototype.pause = function () { this.paused = true; };
  MediaPipeEngine.prototype.resume = function () { this.paused = false; };
  MediaPipeEngine.prototype.stop = function () {
    this.running = false; clearInterval(this._wd);
    if (this.stream) this.stream.getTracks().forEach(function (t) { t.stop(); });
    if (this.video && this.video.parentNode) this.video.parentNode.removeChild(this.video);
    try { this.landmarker && this.landmarker.close(); } catch (e) {}
  };
  MediaPipeEngine.prototype.guidance = function () {
    return Model.poseGuidance(this.lastFeat, { mobile: this.mobile, brightness: this.brightness });
  };
  MediaPipeEngine.prototype.distanceCm = function () { return this.lastFeat ? this.lastFeat.distanceCm : null; };
  MediaPipeEngine.prototype.stats = function () {
    var reg = this.models.current(), m = reg && reg.model;
    return { engine: 'MediaPipe Face Landmarker', delegate: this.delegate, fps: this.fpsWin.length / 2, targetFps: this.fps,
      inferMs: Math.round(this.inferEma * 10) / 10, faceRate: this.frames ? this.faceFrames / this.frames : 0,
      samples: reg ? reg.cal.length : 0, implicit: reg ? reg.implicit.length : 0, lambda: m ? m.lambda : null,
      fitRmsPx: m ? Math.round(m.rmsPx) : null, orientation: this.models.key,
      distanceCm: this.lastFeat && this.lastFeat.distanceCm ? Math.round(this.lastFeat.distanceCm) : null,
      yawDeg: this.lastFeat ? Math.round(this.lastFeat.pose.yaw * 57.3) : null, pitchDeg: this.lastFeat ? Math.round(this.lastFeat.pose.pitch * 57.3) : null };
  };

  /* ----------------------------------------------------------------- WebGazer fallback */
  function WebGazerEngine(opts) {
    this.kind = 'webgazer'; this.opts = opts; this.mobile = isMobile(); this.listeners = []; this.collectT = null;
    this.delegate = 'WebGazer (TF.js)'; this.trained = 0; this.lastPred = null; this.frames = 0; this.faceFrames = 0; this.fpsWin = [];
  }
  WebGazerEngine.prototype.on = MediaPipeEngine.prototype.on;
  WebGazerEngine.prototype.off = MediaPipeEngine.prototype.off;
  WebGazerEngine.prototype._emit = MediaPipeEngine.prototype._emit;
  WebGazerEngine.prototype.load = function () {
    var o = this.opts;
    var load = function (src) {
      return new Promise(function (res, rej) {
        if (window.webgazer) return res();
        var s = document.createElement('script'); s.src = src; s.async = true; s.onload = function () { res(); }; s.onerror = function () { rej(new Error('could not load WebGazer')); };
        document.head.appendChild(s);
      });
    };
    var self = this;
    return load(o.webgazerUrl).catch(function () { return load(o.webgazerCdn); }).then(function () { if (!window.webgazer) throw new Error('gaze engine missing'); return self; });
  };
  WebGazerEngine.prototype.start = function () {
    var self = this, wg = window.webgazer;
    wg.params.showVideo = true; wg.params.showFaceOverlay = true; wg.params.showFaceFeedbackBox = true; wg.params.showGazeDot = false;
    wg.params.videoViewerWidth = 200; wg.params.videoViewerHeight = 150;
    if (wg.saveDataAcrossSessions) wg.saveDataAcrossSessions(false);
    if (wg.applyKalmanFilter) wg.applyKalmanFilter(false);
    try { wg.setRegression('ridge'); } catch (e) {}
    wg.removeMouseEventListeners && wg.removeMouseEventListeners();   // we decide which clicks are training data
    wg.setGazeListener(function (d) {
      var t = Date.now(); self.frames++; self.fpsWin.push(t); while (self.fpsWin.length && t - self.fpsWin[0] > 2000) self.fpsWin.shift();
      if (d) self.faceFrames++;
      self.lastPred = d ? { x: d.x, y: d.y } : null;
      self._emit({ t: t, face: !!d, blink: false, feat: null, pred: self.trained >= 4 ? self.lastPred : null, inferMs: null });
    });
    return wg.begin().then(function () { if (wg.showPredictionPoints) wg.showPredictionPoints(false); self.video = document.getElementById('webgazerVideoFeed'); return self; })
      .catch(function (e) { throw cameraError(e); });
  };
  WebGazerEngine.prototype.beginSample = function (x, y) {
    var wg = window.webgazer; clearInterval(this.collectT);
    this.collectT = setInterval(function () { try { wg.recordScreenPosition(x, y, 'click'); } catch (e) {} }, 120);
  };
  WebGazerEngine.prototype.endSample = function () { clearInterval(this.collectT); this.collectT = null; this.trained++; return 6; };
  WebGazerEngine.prototype.sampleCount = function () { return 99; };
  WebGazerEngine.prototype.resetCalibration = function () { try { window.webgazer.clearData(); } catch (e) {} this.trained = 0; };
  WebGazerEngine.prototype.fit = function () { return this.trained >= 4; };
  WebGazerEngine.prototype.ready = function () { return this.trained >= 4; };
  WebGazerEngine.prototype.implicit = function (x, y) {
    if (!this.lastPred) return null;
    var err = Math.hypot(this.lastPred.x - x, this.lastPred.y - y);
    if (err > 0.35 * Math.hypot(innerWidth, innerHeight)) return { err: err, accepted: false };
    try { window.webgazer.recordScreenPosition(x, y, 'click'); } catch (e) {}
    return { err: err, accepted: true };
  };
  WebGazerEngine.prototype.setOrientation = function () { return this.ready(); };
  WebGazerEngine.prototype.pause = function () { try { window.webgazer.pause(); } catch (e) {} };
  WebGazerEngine.prototype.resume = function () { try { window.webgazer.resume(); } catch (e) {} };
  WebGazerEngine.prototype.stop = function () { try { window.webgazer.clearGazeListener(); window.webgazer.end(); } catch (e) {} };
  WebGazerEngine.prototype.guidance = function () { return { ok: true, checks: [{ key: 'face', ok: true, label: 'Keep your face inside the green box' }] }; };
  WebGazerEngine.prototype.distanceCm = function () { return null; };
  WebGazerEngine.prototype.showPreview = function (on) { try { window.webgazer.showVideoPreview(on); } catch (e) {} };
  WebGazerEngine.prototype.stats = function () {
    return { engine: 'WebGazer (fallback)', delegate: this.delegate, fps: this.fpsWin.length / 2, inferMs: null,
      faceRate: this.frames ? this.faceFrames / this.frames : 0, samples: this.trained, implicit: null, orientation: orientationKey() };
  };

  /* create(): MediaPipe first, WebGazer if MediaPipe cannot load. Camera errors are not retried
     with the fallback (a denied camera is denied for both). */
  function create(opts) {
    opts = opts || {};
    var want = opts.prefer || 'auto';
    var mp = function () { var e = new MediaPipeEngine(opts); return e.load(); };
    var wg = function () { var e = new WebGazerEngine(opts); return e.load(); };
    if (want === 'webgazer') return wg();
    if (want === 'mediapipe') return mp();
    return mp().catch(function (err) {
      if (window.console) console.warn('Helix: MediaPipe unavailable, falling back to WebGazer:', err);
      return wg().then(function (e) { e.fallbackReason = String(err && err.message || err); return e; });
    });
  }

  window.HelixEngine = { create: create, MediaPipeEngine: MediaPipeEngine, WebGazerEngine: WebGazerEngine,
    isMobile: isMobile, orientationKey: orientationKey };
})();
