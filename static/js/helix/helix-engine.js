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

  /* Pass 5 (opt-in): 1080p on desktops with enough cores (the eye-crop stage then gets ~1 camera px per
     crop px; at 720p it upsamples). Falls back to 720p at runtime if the frame budget is missed (_resCheck). */
  function hiResCapable(mobile) {
    var cfg = typeof window !== 'undefined' && window.HELIX_ENGINE || {};
    var qs = typeof location !== 'undefined' ? (location.search || '') : '';
    if (/[?&]hires=0\b/.test(qs) || cfg.hiRes === false) return false;
    var asked = cfg.hiRes || /[?&]hires=1\b/.test(qs);
    if (!asked || mobile || typeof navigator === 'undefined') return false;
    var cores = navigator.hardwareConcurrency || 4, mem = navigator.deviceMemory;
    return cores >= 4 && !(mem && mem < 4);
  }
  function cameraConstraints(mobile, hi) {
    if (hi) return { audio: false, video: { facingMode: 'user', width: { ideal: 1920 }, height: { ideal: 1080 }, frameRate: { ideal: 30, max: 30 } } };
    return {
      audio: false,
      video: {
        facingMode: 'user',                                  // front camera on phones/tablets
        // 720p on laptops: at ~55 cm a 640x480 frame leaves the eyes ~20-30 px wide; the warp
        // benchmark measured 6.8 deg -> 5.7 deg median error for the same face at 1280x720.
        // Phones are held closer (eyes are already large), so stay at 480x640 to save CPU/heat.
        width: { ideal: mobile ? 480 : 1280 }, height: { ideal: mobile ? 640 : 720 },
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
  function isIOS() { return /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1); }
  function isAndroid() { return /Android/i.test(navigator.userAgent); }
  // WebAssembly SIMD probe (tiny module using v128); MediaPipe's loader picks the no-SIMD build
  // itself, this is only reported so a slow device can be explained in the diagnostics.
  function simdSupported() {
    try { return WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11])); } catch (e) { return false; }
  }
  /* Open the camera *inside* the click/tap handler (before any await): iOS Safari and some
     Android builds only show the permission prompt / allow playback from a user gesture. */
  var pendingStream = null;
  function prefetchCamera(mobile) {
    if (pendingStream || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return pendingStream;
    var m = mobile == null ? isMobile() : mobile;
    pendingStream = navigator.mediaDevices.getUserMedia(cameraConstraints(m, hiResCapable(m))).catch(function (e) {
      if (/Overconstrained/i.test(String(e && e.name))) return navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'user' } });
      throw e;
    });
    pendingStream.catch(function () { pendingStream = null; });
    return pendingStream;
  }
  // a prefetched stream that ends up unused (e.g. MediaPipe failed and WebGazer opens its own) must be closed
  function releasePrefetch() {
    var p = pendingStream; pendingStream = null;
    if (p) p.then(function (st) { st.getTracks().forEach(function (t) { t.stop(); }); }, function () {});
  }
  function takeStream(mobile) { var p = pendingStream || prefetchCamera(mobile); pendingStream = null; return p; }
  function hiResWanted(mobile) { return hiResCapable(mobile == null ? isMobile() : mobile); }

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
    this.poseWin = [];
    this.recent = [];              // last ~1 s of features, for implicit samples
    this.collect = null;           // active calibration collection
    this.maxFps = this.mobile ? 24 : 30; this.minFps = 6; this.fps = this.maxFps;
    this.inferEma = 0; this.frames = 0; this.faceFrames = 0; this.fpsWin = [];
    this.paused = false; this.running = false; this.lastFeat = null; this.delegate = null;
    this.brightness = null; this.quality = { brightness: null, contrast: null, glare: null, faces: 0 };
    this.blinkGate = new Model.BlinkGate();
    this.primary = null;           // locked face (centre/size) when several faces are in view
    this.eyeBase = null; this.calPose = null; this.calViewport = null;
    this.thermal = { base: null, t0: 0, hot: false };
    this.ios = isIOS(); this.android = isAndroid(); this.simd = simdSupported();
    this.occluded = null; this.rejected = { blink: 0, occluded: 0, otherFace: 0 };
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
          // 2 faces so a second person (sibling, classmate on the couch) can be ignored instead of
          // silently swapping who is tracked; _pickFace() locks onto the student
          runningMode: 'VIDEO', numFaces: o.numFaces || 2, minFaceDetectionConfidence: 0.5, minTrackingConfidence: 0.5,
          outputFacialTransformationMatrixes: true, outputFaceBlendshapes: true
        }).then(function (lm) { self.delegate = delegate; return lm; });
      };
      var order = o.delegate === 'CPU' ? ['CPU'] : ['GPU', 'CPU'];   // GPU (WebGL) first, CPU (WASM) fallback
      return order.reduce(function (p, d) { return p.catch(function () { return make(d); }); }, Promise.reject(new Error('start')));
    }).then(function (lm) { self.landmarker = lm; return self; }, function (e) {
      // iOS (≈1.5 GB tab limit) and old Android can run out of memory compiling the WASM/model
      var msg = String(e && (e.message || e));
      var err = new Error(/memory|allocation|RangeError/i.test(msg) ? 'not enough memory for the face model on this device' : msg);
      err.code = 'load_failed'; throw err;
    });
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
    this.hiRes = hiResWanted(this.mobile);
    return takeStream(this.mobile).then(function (stream) {
      self.stream = stream; v.srcObject = stream;
      return v.play().catch(function (e) {
        // autoplay policy (iOS Low Power Mode, some in-app browsers): needs another tap
        if (e && e.name === 'NotAllowedError') { var err = new Error('tap to start the camera'); err.code = 'play_blocked'; err.name = 'PlayBlocked'; throw err; }
      });
    }).then(function () {
      return new Promise(function (res) { if (v.videoWidth) res(); else v.addEventListener('loadedmetadata', function () { res(); }, { once: true }); });
    }).then(function () {
      self.running = true; self._loop(); self._watchBattery(); self._watchCamera(); return self;
    }).catch(function (e) { if (e && e.code === 'play_blocked') throw e; throw cameraError(e); });
  };

  /* Pass 10 session hardening: notice when the camera goes away mid-session instead of silently
     reporting "face not found" forever. Sources, each reported once as {notice: 'camera_lost', reason}:
       'ended'      the track ended (camera unplugged, driver reset, OS took it, laptop lid closed)
       'permission' camera permission changed to denied (Permissions API, where supported)
       'unplugged'  devicechange and our camera is no longer listed
       'muted'      the track stayed muted for 4 s (privacy shutter, another app; unmute clears it)
     A video track's readyState is also checked by the frame watchdog, which catches sleep/resume
     cases where no event fires. Nothing here touches pixels. */
  MediaPipeEngine.prototype._watchCamera = function () {
    var self = this, tr = this.stream && this.stream.getVideoTracks ? this.stream.getVideoTracks()[0] : null;
    this.lost = null; this._muteT = 0;
    if (!tr) return;
    this.track = tr;
    try { this.deviceId = (tr.getSettings && tr.getSettings().deviceId) || null; } catch (e) { this.deviceId = null; }
    var onEnded = function () { self._cameraLost('ended'); };
    var onMute = function () { clearTimeout(self._muteT); self._muteT = setTimeout(function () { if (tr.muted) self._cameraLost('muted'); }, 4000); };
    var onUnmute = function () { clearTimeout(self._muteT); if (self.lost === 'muted') { self.lost = null; self._emit({ t: Date.now(), notice: 'camera_back', face: false, feat: null, pred: null }); } };
    tr.addEventListener('ended', onEnded); tr.addEventListener('mute', onMute); tr.addEventListener('unmute', onUnmute);
    this._unwatch = function () { tr.removeEventListener('ended', onEnded); tr.removeEventListener('mute', onMute); tr.removeEventListener('unmute', onUnmute); clearTimeout(self._muteT); };
    if (navigator.permissions && navigator.permissions.query && !this._permWatched) {
      this._permWatched = true;
      navigator.permissions.query({ name: 'camera' }).then(function (st) {
        self._perm = st;
        var upd = function () { if (st.state === 'denied') self._cameraLost('permission'); };
        if (st.addEventListener) st.addEventListener('change', upd); else st.onchange = upd;
      }).catch(function () {});
    }
    if (navigator.mediaDevices && navigator.mediaDevices.addEventListener && !this._devWatched) {
      this._devWatched = true;
      navigator.mediaDevices.addEventListener('devicechange', function () {
        if (!self.running || !self.deviceId || !navigator.mediaDevices.enumerateDevices) return;
        navigator.mediaDevices.enumerateDevices().then(function (list) {
          var still = list.some(function (d) { return d.kind === 'videoinput' && d.deviceId === self.deviceId; });
          if (!still) self._cameraLost('unplugged');
        }).catch(function () {});
      });
    }
  };
  MediaPipeEngine.prototype._cameraLost = function (reason) {
    if (this.lost && this.lost !== 'muted') return;     // first hard reason wins
    this.lost = reason;
    if (reason !== 'muted') {
      // release whatever is left of the stream so the camera light goes off
      try { if (this.stream) this.stream.getTracks().forEach(function (t) { t.stop(); }); } catch (e) {}
    }
    this.lastFeat = null;
    this._emit({ t: Date.now(), notice: 'camera_lost', reason: reason, face: false, feat: null, pred: null });
  };
  /* Re-open the camera after a loss. Prefers the same device; reports whether it got it, because a
     different camera (or the same one moved) invalidates the calibration. */
  MediaPipeEngine.prototype.reconnect = function () {
    var self = this, want = this.deviceId;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return Promise.reject(new Error('camera not available'));
    var c = cameraConstraints(this.mobile, hiResCapable(this.mobile));
    if (want) c.video.deviceId = { ideal: want };
    if (this._unwatch) this._unwatch();
    return navigator.mediaDevices.getUserMedia(c).then(function (stream) {
      self.stream = stream; self.video.srcObject = stream;
      return self.video.play().catch(function () {});
    }).then(function () {
      var prev = self.deviceId;
      self._watchCamera();
      if (!self.running) { self.running = true; self._loop(); }
      return { sameDevice: !!(prev && self.deviceId === prev) || !prev };
    }).catch(function (e) { throw cameraError(e); });
  };
  /* retry playback from a user gesture after 'play_blocked' */
  MediaPipeEngine.prototype.resumePlayback = function () {
    var self = this, v = this.video;
    return v.play().then(function () { if (!self.running) { self.running = true; self._loop(); self._watchBattery(); } return self; });
  };

  MediaPipeEngine.prototype._watchBattery = function () {
    var self = this;
    if (!navigator.getBattery) return;
    navigator.getBattery().then(function (b) {
      var upd = function () { var base = self.mobile ? 24 : 30; if (self.thermal.hot) base = Math.max(self.minFps, Math.round(base * 0.6)); self.lowBattery = !b.charging && b.level < 0.25; self.maxFps = self.lowBattery ? Math.min(10, base) : base; if (self.fps > self.maxFps) self.fps = self.maxFps; };
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
    this._wd = setInterval(function () {
      // sleep/resume can end the track without an 'ended' event in some browsers
      if (self.track && self.track.readyState === 'ended' && !self.lost) { self._cameraLost('ended'); return; }
      if (self.running && Date.now() - self._lastStep > 600) { pending = false; step(); }
    }, 300);
    var step = function () {
      pending = false; self._lastStep = Date.now();
      if (!self.running) return;
      var t = nowMs();
      if (self.paused || self.lost || document.hidden || t - last < 1000 / self.fps - 2) { schedule(); return; }
      last = t;
      self._process(t);
      schedule();
    };
    schedule();
  };

  MediaPipeEngine.prototype._process = function (t) {
    var res, v = this.video;
    var t0 = nowMs();
    // optional: run face detection/landmarks on a downscaled copy (cheap on 1080p cameras); the
    // eye-crop stage below still samples the full-resolution frame
    var src = v, dw = this.opts.detectWidth;
    if (dw && v.videoWidth > dw * 1.1) {
      var dc = this._detCanvas || (this._detCanvas = document.createElement('canvas'));
      var dh = Math.round(dw * v.videoHeight / v.videoWidth);
      if (dc.width !== dw || dc.height !== dh) { dc.width = dw; dc.height = dh; }
      dc.getContext('2d').drawImage(v, 0, 0, dw, dh); src = dc;
    }
    try { res = this.landmarker.detectForVideo(src, t); } catch (e) { return; }
    var infer = nowMs() - t0;
    this.inferEma = this.inferEma ? this.inferEma * 0.9 + infer * 0.1 : infer;
    // thermal/battery friendly: frame budget adapts to how long inference takes on this device
    var budget = 1000 / this.fps;
    if ((this.inferEma > budget * 0.7 || (this.mobile && this.inferEma > 22 && this.fps > 15)) && this.fps > this.minFps) this.fps = Math.max(this.minFps, this.fps - 2);
    else if (this.inferEma < (this.mobile ? Math.min(22, budget * 0.45) : budget * 0.35) && this.fps < this.maxFps) this.fps = Math.min(this.maxFps, this.fps + 1);
    this.frames++;
    this.fpsWin.push(t); while (this.fpsWin.length && t - this.fpsWin[0] > 2000) this.fpsWin.shift();
    this._thermalCheck(t);
    this._resCheck();
    var n = res && res.faceLandmarks ? res.faceLandmarks.length : 0;
    var k = n ? this._pickFace(res.faceLandmarks, t) : -1;
    var lm = k >= 0 ? res.faceLandmarks[k] : null;
    if (n > 1 && k !== 0) this.rejected.otherFace++;
    this.quality.faces = n;
    var feat = null;
    if (lm) {
      var mat = res.facialTransformationMatrixes && res.facialTransformationMatrixes[k];
      var bsc = res.faceBlendshapes && res.faceBlendshapes[k];
      feat = Model.eyeFeatures(lm, v.videoWidth, v.videoHeight, mat && mat.data, { blendshapes: bsc && bsc.categories, hfovDeg: this.opts.hfovDeg });
      if (feat) { this.faceFrames++; feat.landmarks = lm; }
      if (feat && this._cropOn()) this._cropStage(feat, lm);
    }
    if (!feat) this.lastCrops = null;      // never show a stale crop when the face is lost
    if (this.frames % 10 === 1) this._measureQuality(lm);
    var wall = Date.now();
    if (feat) {
      // temporal blink gate: a blink is a short closure relative to this person's own openness;
      // long narrowing (looking down at the page) is kept
      feat.staticBlink = feat.blink;
      feat.blink = this.blinkGate.update(feat, t);
      if (feat.blink) this.rejected.blink++;
      var q = Model.eyeQuality(feat, this.eyeBase);
      feat.occluded = q.ok ? null : q.reason;
      if (feat.occluded && this.eyeBase) this.rejected.occluded++;
    }
    this.occluded = feat ? feat.occluded : null;
    this.lastFeat = feat;
    var usable = feat && !feat.blink && !(feat.occluded && this.eyeBase);
    if (usable) {
      this.recent.push({ t: wall, feat: feat }); while (this.recent.length && wall - this.recent[0].t > 1200) this.recent.shift();
      if (this.collect && wall >= this.collect.from) this.collect.samples.push(feat);
      if (this.collect && this.collect.path) this.collect.rows.push({ t: wall, vec: feat.vec, feat: feat });
      this.poseWin.push({ t: wall, feat: feat }); while (this.poseWin.length && wall - this.poseWin[0].t > 4000) this.poseWin.shift();
    }
    var reg = this.models.current(), pred = null;
    if (usable && reg && reg.model) {
      pred = reg.predict(feat.vec);
      var sh = this.calViewport && typeof window !== 'undefined' ? Model.viewportShift(this.calViewport, { w: window.innerWidth, h: window.innerHeight }, { topBar: this.android }) : 0;
      if (sh) pred.y += sh;
      pred = clampPred(pred);
    }
    this._emit({ t: wall, face: !!feat, blink: !!(feat && feat.blink), occluded: feat ? feat.occluded : null, faces: n, feat: feat, pred: pred, inferMs: infer, quality: this.quality });
  };

  /* Several faces: keep the one we locked onto (closest to its last position, then largest).
     The lock follows the student as they move; it is only released after ~1 s without them. */
  MediaPipeEngine.prototype._pickFace = function (faces, t) {
    var info = faces.map(function (lm, i) {
      var xs = lm[234], xe = lm[454], top = lm[10], chin = lm[152];
      return { i: i, x: (xs.x + xe.x) / 2, y: (top.y + chin.y) / 2, w: Math.abs(xe.x - xs.x) };
    });
    var now = t || nowMs(), p = this.primary, pick = null;
    if (p && now - p.t < 1000) {
      info.forEach(function (f) { var d = Math.hypot(f.x - p.x, f.y - p.y); if (d < 0.25 + p.w && (!pick || d < pick.d)) pick = { f: f, d: d }; });
      pick = pick && pick.f;
    }
    if (!pick) info.forEach(function (f) { if (!pick || f.w > pick.w) pick = f; });
    this.primary = { x: pick.x, y: pick.y, w: pick.w, t: now };
    return pick.i;
  };

  /* Light and glare from the pixels the tracker actually uses: mean/contrast of the face box and
     the share of blown-out pixels around the eyes (glasses reflections). Runs every 10th frame
     on a 64-px thumbnail, so it costs well under 1 ms. Nothing leaves the device. */
  MediaPipeEngine.prototype._measureQuality = function (lm) {
    try {
      var v = this.video, W = v.videoWidth, H = v.videoHeight;
      var c = this._qc || (this._qc = document.createElement('canvas')), g = c.getContext('2d', { willReadFrequently: true });
      var box = lm ? [lm[234].x, lm[10].y, lm[454].x, lm[152].y] : [0.3, 0.2, 0.7, 0.8];
      var x0 = Math.max(0, Math.min(box[0], box[2]) * W), y0 = Math.max(0, box[1] * H), x1 = Math.min(W, Math.max(box[0], box[2]) * W), y1 = Math.min(H, box[3] * H);
      if (x1 - x0 < 8 || y1 - y0 < 8) return;
      c.width = 64; c.height = 64; g.drawImage(v, x0, y0, x1 - x0, y1 - y0, 0, 0, 64, 64);
      var d = g.getImageData(0, 0, 64, 64).data, s = 0, s2 = 0, n = d.length / 4;
      for (var i = 0; i < d.length; i += 4) { var L = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]; s += L; s2 += L * L; }
      var mean = s / n;
      this.quality.brightness = Math.round(mean); this.quality.contrast = Math.round(Math.sqrt(Math.max(0, s2 / n - mean * mean)));
      this.brightness = this.quality.brightness;
      if (lm) {
        var gl = 0, tot = 0, eyes = [[33, 133, 159, 145], [362, 263, 386, 374]];
        for (var e = 0; e < 2; e++) {
          var a = lm[eyes[e][0]], b = lm[eyes[e][1]], ew = Math.abs(b.x - a.x) * W;
          var cx = (a.x + b.x) / 2 * W, cy = (lm[eyes[e][2]].y + lm[eyes[e][3]].y) / 2 * H;
          c.width = 24; c.height = 16; g.drawImage(v, cx - ew, cy - ew * 0.65, ew * 2, ew * 1.3, 0, 0, 24, 16);
          var q = g.getImageData(0, 0, 24, 16).data;
          for (var j = 0; j < q.length; j += 4) { tot++; if (q[j] > 245 && q[j + 1] > 245 && q[j + 2] > 245) gl++; }
        }
        this.quality.glare = tot ? Math.round(1000 * gl / tot) / 1000 : null;
      }
    } catch (err) { /* tainted canvas or zero-size video */ }
  };
  MediaPipeEngine.prototype._measureBrightness = function () { this._measureQuality(this.lastFeat && this.lastFeat.landmarks); };

  /* Thermal / low-end CPU back-off: if inference becomes much slower than it was in the first
     20 s (the phone is heating up and throttling), cap the frame rate harder and say so. */
  /* adaptive resolution: a 1080p stream that pushes inference + crops past ~20 fps drops to 720p once */
  MediaPipeEngine.prototype._resCheck = function () {
    if (this._resDown || this.frames < 90 || !this.video || this.video.videoWidth <= 1280) return;
    if (this.inferEma + (this.cropMsEma || 0) <= 1000 / 20) return;
    var tr = this.stream && this.stream.getVideoTracks && this.stream.getVideoTracks()[0];
    this._resDown = true;
    if (tr && tr.applyConstraints) tr.applyConstraints({ width: { ideal: 1280 }, height: { ideal: 720 } }).catch(function () {});
    this._emit({ t: Date.now(), notice: 'res_down', face: !!this.lastFeat, feat: this.lastFeat, pred: null });
  };
  MediaPipeEngine.prototype._thermalCheck = function (t) {
    var th = this.thermal;
    if (!th.t0) th.t0 = t;
    if (!th.base && t - th.t0 > 20000 && this.inferEma) th.base = this.inferEma;
    if (th.base && !th.hot && this.inferEma > th.base * 1.7 && this.inferEma > 30) {
      th.hot = true; this.maxFps = Math.max(this.minFps, Math.round(this.maxFps * 0.6)); if (this.fps > this.maxFps) this.fps = this.maxFps;
      this._emit({ t: Date.now(), notice: 'thermal', face: !!this.lastFeat, feat: this.lastFeat, pred: null });
    }
  };

  /* Low light: ask the camera for continuous auto-exposure (and a little exposure compensation)
     where the browser exposes it (Chrome on Android/desktop). Returns what was applied. */
  MediaPipeEngine.prototype.exposureHint = function () {
    var tr = this.stream && this.stream.getVideoTracks()[0];
    if (!tr || !tr.getCapabilities) return Promise.resolve(null);
    var cap = tr.getCapabilities(), adv = {};
    if (cap.exposureMode && cap.exposureMode.indexOf('continuous') >= 0) adv.exposureMode = 'continuous';
    if (cap.exposureCompensation && cap.exposureCompensation.max > 0) adv.exposureCompensation = Math.min(cap.exposureCompensation.max, 1);
    if (cap.whiteBalanceMode && cap.whiteBalanceMode.indexOf('continuous') >= 0) adv.whiteBalanceMode = 'continuous';
    if (!Object.keys(adv).length) return Promise.resolve(null);
    return tr.applyConstraints({ advanced: [adv] }).then(function () { return adv; }, function () { return null; });
  };

  /* Should we recalibrate? Compares the last ~4 s of head pose with the calibration snapshot. */
  /* ---- second stage: full-resolution eye crops (see HelixModel.cropEyeFeatures) ----
     opts.crop: 'view' = compute crops for the diagnostics HUD only (Try page), model unchanged;
                true   = also append the 8 crop features to vec (experimental: the pass-5 warp A/B
                         did not show a consistent gain, see tools/helix_eval/RESULTS.md);
                falsy  = off (default). Phones only run it when explicitly forced with true.
     Switches itself off if inference + crops no longer fit ~12 fps. */
  MediaPipeEngine.prototype._cropOn = function () {
    var o = this.opts.crop;
    if (!o || this.cropDisabled || !this.video || this.video.videoWidth < 320) return false;
    return !(this.mobile && o !== true);
  };
  MediaPipeEngine.prototype._cropStage = function (feat, lm) {
    var t0 = nowMs(), v = this.video, W = v.videoWidth, H = v.videoHeight, CW = Model.CROP.W, CH = Model.CROP.H;
    var c = this._cropCanvas || (this._cropCanvas = document.createElement('canvas'));
    if (c.width !== CW || c.height !== CH) { c.width = CW; c.height = CH; }
    var g = c.getContext('2d', { willReadFrequently: true });
    var P = function (i) { return [lm[i].x * W, lm[i].y * H]; };
    var out = {}, self = this, pw = this.opts.patch || [15, 9];
    [['r', 33, 133, Model.R_CONTOUR], ['l', 362, 263, Model.L_CONTOUR]].forEach(function (e) {
      var T = Model.eyeCropTransform(P(e[1]), P(e[2]));
      g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#808080'; g.fillRect(0, 0, CW, CH);
      g.setTransform(T.a, T.b, T.c, T.d, T.e, T.f); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
      try { g.drawImage(v, 0, 0); } catch (err) { return; }
      g.setTransform(1, 0, 0, 1, 0, 0);
      var d = g.getImageData(0, 0, CW, CH).data, gray = new Float32Array(CW * CH);
      for (var i = 0, j = 0; i < gray.length; i++, j += 4) gray[i] = 0.299 * d[j] + 0.587 * d[j + 1] + 0.114 * d[j + 2];
      var poly = e[3].map(function (k) { return T.apply(P(k)); });
      var f = Model.cropEyeFeatures(gray, CW, CH, poly, { patch: pw, noTB: self.opts.cropTB === false });
      f.nativeScale = 1 / T.scale;     // > 1: the crop is downsampling the camera (more detail than MediaPipe saw)
      out[e[0]] = f;
      if (self.keepCrops) (self.lastCrops || (self.lastCrops = {}))[e[0]] = { gray: gray, poly: poly, tb: f.tb, dc: f.dc };
    });
    out.ms = nowMs() - t0;
    this.cropMsEma = this.cropMsEma ? this.cropMsEma * 0.9 + out.ms * 0.1 : out.ms;
    // graceful degradation: if inference + crops no longer fit the frame budget at >= 12 fps, drop the stage
    if (this.frames > 60 && this.inferEma + this.cropMsEma > 1000 / 12) { this.cropDisabled = true; this._emit({ t: Date.now(), notice: 'crop_off', face: true, feat: feat, pred: null }); }
    feat.crop = out;
    if (this.opts.crop === true) feat.vec = feat.vec.concat(Model.cropVec(out));   // GazeRegressor adds these to stage 2 when present
  };

  MediaPipeEngine.prototype.recalCheck = function () {
    if (!this.calPose || this.poseWin.length < 8) return null;
    return Model.recalTrigger(this.calPose, Model.poseSnapshot(this.poseWin.map(function (r) { return r.feat; })));
  };


  /* calibration: collect features while the student looks at (x, y) */
  MediaPipeEngine.prototype.beginSample = function (x, y, settleMs) { this.collect = { x: x, y: y, from: Date.now() + (settleMs || 250), samples: [] }; };
  MediaPipeEngine.prototype.endSample = function () {
    var c = this.collect; this.collect = null;
    if (!c) return 0;
    var reg = this.models.current();
    c.samples.forEach(function (f) { reg.addCalibration(f.vec, c.x, c.y); });
    this.calFeats = (this.calFeats || []).concat(c.samples);
    return c.samples.length;
  };
  /* smooth pursuit: record features while a dot moves along `path` ({t,x,y} pushed by the UI) */
  MediaPipeEngine.prototype.beginPursuit = function () { this.collect = { from: Date.now(), samples: [], rows: [], path: [] }; return this.collect.path; };
  MediaPipeEngine.prototype.endPursuit = function () {
    var c = this.collect; this.collect = null;
    if (!c || !c.path) return null;
    var fit = Model.fitPursuit(c.rows, c.path, { weight: 0.7 });
    if (!fit) return null;
    var reg = this.models.current();
    fit.pairs.forEach(function (p) { reg.addCalibration(p.vec, p.x, p.y, 0.7); });
    this.calFeats = (this.calFeats || []).concat(c.rows.map(function (r) { return r.feat; }));
    return { lagMs: fit.lag, samples: fit.pairs.length, rmsPx: Math.round(fit.rms) };
  };
  MediaPipeEngine.prototype.sampleCount = function () { return this.collect ? this.collect.samples.length : 0; };
  MediaPipeEngine.prototype.resetCalibration = function () { var reg = this.models.current(); reg.cal = []; reg.model = null; this.calFeats = []; };
  MediaPipeEngine.prototype.fit = function () {
    var m = this.models.current().fit();
    if (m && this.calFeats && this.calFeats.length) {
      // references for occlusion checks, recalibration triggers and the mobile URL-bar shift
      this.eyeBase = Model.eyeBaseline(this.calFeats);
      this.calPose = Model.poseSnapshot(this.calFeats);
      if (typeof window !== 'undefined') this.calViewport = { w: window.innerWidth, h: window.innerHeight };
    }
    return !!m;
  };
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
    this.running = false; clearInterval(this._wd); if (this._unwatch) this._unwatch();
    if (this.stream) this.stream.getTracks().forEach(function (t) { t.stop(); });
    if (this.video && this.video.parentNode) this.video.parentNode.removeChild(this.video);
    try { this.landmarker && this.landmarker.close(); } catch (e) {}
  };
  MediaPipeEngine.prototype.guidance = function () {
    return Model.poseGuidance(this.lastFeat, { mobile: this.mobile, brightness: this.brightness, quality: this.quality });
  };
  MediaPipeEngine.prototype.distanceCm = function () { return this.lastFeat ? this.lastFeat.distanceCm : null; };
  MediaPipeEngine.prototype.stats = function () {
    var reg = this.models.current(), m = reg && reg.model;
    return { engine: 'MediaPipe Face Landmarker', delegate: this.delegate, fps: this.fpsWin.length / 2, targetFps: this.fps,
      inferMs: Math.round(this.inferEma * 10) / 10, faceRate: this.frames ? this.faceFrames / this.frames : 0,
      samples: reg ? reg.cal.length : 0, implicit: reg ? reg.implicit.length : 0, lambda: m ? m.lambda : null,
      fitRmsPx: m ? Math.round(m.rmsPx) : null, orientation: this.models.key, modelCrop: m ? !!m.crop : null, lambdaSel: m ? m.lambdaSel : null,
      faces: this.quality.faces, brightness: this.quality.brightness, contrast: this.quality.contrast, glare: this.quality.glare,
      occluded: this.occluded, thermal: this.thermal.hot, lowBattery: !!this.lowBattery, simd: this.simd, rejected: this.rejected,
      resolution: this.video ? this.video.videoWidth + 'x' + this.video.videoHeight + (this._resDown ? ' (lowered: too slow)' : '') : null,
      videoW: this.video ? this.video.videoWidth : null, videoH: this.video ? this.video.videoHeight : null,
      hiRes: !!this.hiRes, resDown: !!this._resDown, cameraLost: this.lost || null,
      crop: this._cropOn() ? (this.opts.crop === true ? 'features' : 'view only') + (this.cropMsEma ? ', ' + Math.round(this.cropMsEma * 10) / 10 + ' ms/frame' : '') : (this.cropDisabled ? 'off (too slow)' : 'off'),
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
    return load(o.webgazerUrl).catch(function (e) { if (o.webgazerCdn) return load(o.webgazerCdn); throw e; }).then(function () { if (!window.webgazer) throw new Error('gaze engine missing'); return self; });
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
    var wg = function () { releasePrefetch(); var e = new WebGazerEngine(opts); return e.load(); };
    if (want === 'webgazer') return wg();
    if (want === 'mediapipe') return mp();
    return mp().catch(function (err) {
      if (window.console) console.warn('Helix: MediaPipe unavailable, falling back to WebGazer:', err);
      return wg().then(function (e) { e.fallbackReason = String(err && err.message || err); return e; });
    });
  }

  window.HelixEngine = { create: create, MediaPipeEngine: MediaPipeEngine, WebGazerEngine: WebGazerEngine,
    isMobile: isMobile, orientationKey: orientationKey, prefetchCamera: prefetchCamera, hiResCapable: hiResCapable, releasePrefetch: releasePrefetch, isIOS: isIOS, simdSupported: simdSupported };
})();
