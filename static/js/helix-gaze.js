/* CIWT Helix gaze — WebGazer engine.
   Opt-in attention signal only. Never a grade.
   Stores compact AOI timelines on the LMS, not raw video. */
(function () {
  'use strict';
  var CFG = window.HELIX || {};
  if (!CFG.lessonId) return;

  var POLICY_VERSION = CFG.policyVersion || '2026-09-06';
  var STORAGE_KEY = 'ciwt-helix-consent-' + POLICY_VERSION;
  var sessionId = null;
  var running = false;
  var calibrated = false;
  var flushTimer = null;
  var current = { key: null, label: null, t0: 0, n: 0, conf: 0 };
  var pending = [];
  var dwell = {};
  var startedAt = 0;
  var sampleCount = 0;
  var lastFlush = 0;

  function $(id) { return document.getElementById(id); }
  function now() { return Date.now(); }
  function slug(s) {
    return String(s || '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 48) || 'block';
  }

  function tagAois() {
    var body = $('lessonBody');
    if (!body) return [];
    var heads = Array.prototype.slice.call(body.querySelectorAll('h2,h3,h4,h5'));
    var list = [];
    heads.forEach(function (h, i) {
      var label = (h.textContent || '').replace(/\s+/g, ' ').trim();
      if (!label) return;
      var key = 'h' + i + '-' + slug(label);
      h.setAttribute('data-aoi', key);
      h.setAttribute('data-aoi-label', label);
      h.setAttribute('data-aoi-order', String(i));
      var el = h.nextElementSibling;
      while (el && !/^H[2-5]$/.test(el.tagName)) {
        el.setAttribute('data-aoi', key);
        el.setAttribute('data-aoi-label', label);
        el.setAttribute('data-aoi-order', String(i));
        el = el.nextElementSibling;
      }
      list.push({ key: key, label: label, order: i });
    });
    if (!list.length) {
      body.setAttribute('data-aoi', 'lesson-body');
      body.setAttribute('data-aoi-label', 'Lesson body');
      body.setAttribute('data-aoi-order', '0');
      list.push({ key: 'lesson-body', label: 'Lesson body', order: 0 });
    }
    return list;
  }

  function hitAoi(x, y) {
    if (x == null || y == null || x < 0 || y < 0) {
      return { key: 'off_page', label: 'Off page', order: 999 };
    }
    var node = document.elementFromPoint(x, y);
    while (node && node.getAttribute && !node.getAttribute('data-aoi')) {
      node = node.parentElement;
    }
    if (node && node.getAttribute) {
      return {
        key: node.getAttribute('data-aoi'),
        label: node.getAttribute('data-aoi-label') || node.getAttribute('data-aoi'),
        order: parseInt(node.getAttribute('data-aoi-order') || '0', 10) || 0
      };
    }
    var body = $('lessonBody');
    if (body) {
      var r = body.getBoundingClientRect();
      if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) {
        return { key: 'lesson-body', label: 'Lesson body', order: 0 };
      }
    }
    return { key: 'chrome', label: 'Page chrome', order: 998 };
  }

  function closeSegment(t) {
    if (!current.key) return;
    var dur = Math.max(0, t - current.t0);
    if (dur < 80 && current.n < 2) {
      current = { key: null, label: null, t0: t, n: 0, conf: 0 };
      return;
    }
    var t0rel = current.t0 - startedAt;
    pending.push({
      t0: Math.max(0, t0rel),
      t1: Math.max(0, t - startedAt),
      aoi: current.key,
      label: current.label,
      n: current.n,
      conf: current.n ? Math.round((current.conf / current.n) * 100) / 100 : 0
    });
    var b = dwell[current.key] || {
      aoi_key: current.key,
      aoi_label: current.label,
      aoi_order: current.order || 0,
      dwell_ms: 0,
      visits: 0,
      first_ms: t0rel,
      last_ms: t - startedAt
    };
    if (!dwell[current.key]) b.visits = 1;
    else b.visits += 1;
    b.dwell_ms += dur;
    b.last_ms = t - startedAt;
    dwell[current.key] = b;
    current = { key: null, label: null, t0: t, n: 0, conf: 0 };
  }

  function onGaze(data) {
    if (!running || !calibrated) return;
    var t = now();
    sampleCount += 1;
    var hit;
    if (!data) hit = { key: 'off_page', label: 'Off page', order: 999 };
    else hit = hitAoi(data.x, data.y);
    var dot = $('helixGazeDot');
    if (dot && data) {
      dot.style.left = data.x + 'px';
      dot.style.top = data.y + 'px';
      dot.style.display = 'block';
    }
    if (hit.key !== current.key) {
      closeSegment(t);
      current = {
        key: hit.key,
        label: hit.label,
        order: hit.order,
        t0: t,
        n: 1,
        conf: 1
      };
    } else {
      current.n += 1;
      current.conf += 1;
    }
    var hud = $('helixHud');
    if (hud && sampleCount % 8 === 0) {
      hud.textContent = hit.label;
    }
  }

  function postJSON(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(body || {})
    }).then(function (r) { return r.json().catch(function () { return {}; }); });
  }

  function flush(forceEnd) {
    if (!sessionId) return Promise.resolve();
    closeSegment(now());
    var segs = pending.splice(0, pending.length);
    var buckets = Object.keys(dwell).map(function (k) { return dwell[k]; });
    if (!segs.length && !forceEnd) return Promise.resolve();
    var url = (CFG.timelineUrl || '/api/helix/session/0/timeline').replace('/0/', '/' + sessionId + '/');
    return postJSON(url, {
      segments: segs.slice(0, 250),
      buckets: buckets,
      sample_count: sampleCount,
      viewport_w: window.innerWidth,
      viewport_h: window.innerHeight,
      end: !!forceEnd
    });
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.webgazer) return resolve();
      var s = document.createElement('script');
      s.src = src;
      s.async = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error('load failed ' + src)); };
      document.head.appendChild(s);
    });
  }

  function startEngine() {
    var local = CFG.engineUrl;
    var cdn = CFG.cdnUrl || 'https://cdn.jsdelivr.net/npm/webgazer@3.3.0/dist/webgazer.min.js';
    return loadScript(local).catch(function () { return loadScript(cdn); }).then(function () {
      if (!window.webgazer) throw new Error('WebGazer missing');
      webgazer.params.showVideo = false;
      webgazer.params.showFaceOverlay = false;
      webgazer.params.showFaceFeedbackBox = false;
      webgazer.params.showGazeDot = false;
      if (webgazer.showVideoPreview) webgazer.showVideoPreview(false);
      if (webgazer.showPredictionPoints) webgazer.showPredictionPoints(false);
      if (webgazer.applyKalmanFilter) webgazer.applyKalmanFilter(true);
      if (webgazer.saveDataAcrossSessions) webgazer.saveDataAcrossSessions(false);
      webgazer.setGazeListener(function (data) { onGaze(data); });
      return webgazer.begin();
    });
  }

  function showCalib() {
    var overlay = $('helixCalib');
    if (overlay) overlay.classList.remove('d-none');
    var pts = overlay.querySelectorAll('[data-cal]');
    var saved = 0;
    pts.forEach(function (btn) {
      btn.onclick = function () {
        var r = btn.getBoundingClientRect();
        var x = r.left + r.width / 2;
        var y = r.top + r.height / 2;
        try {
          if (window.webgazer && webgazer.recordScreenPosition) {
            webgazer.recordScreenPosition(x, y, 'click');
          }
        } catch (e) {}
        btn.classList.add('saved');
        btn.textContent = 'Saved';
        saved += 1;
        if (saved >= pts.length) {
          calibrated = true;
          overlay.classList.add('d-none');
          var st = $('helixStatus');
          if (st) st.textContent = 'Gaze live — attention signal only';
          var calUrl = (CFG.calibratedUrl || '/api/helix/session/0/calibrated').replace('/0/', '/' + sessionId + '/');
          postJSON(calUrl, {
            calibration_points: saved,
            calibration_score: 80
          }).catch(function () {});
        }
      };
    });
  }

  function buildChrome() {
    if ($('helixDock')) return;
    var dock = document.createElement('div');
    dock.id = 'helixDock';
    dock.innerHTML =
      '<div class="helix-dock-card">' +
      '<div class="helix-dock-top">' +
      '<strong>Helix attention</strong>' +
      '<span class="helix-pill">Not a grade</span>' +
      '</div>' +
      '<p class="helix-copy">Optional camera signal of where your eyes linger on this lesson. CIWT does not use it as a score, pass/fail, or attendance mark. Face video stays in this browser.</p>' +
      '<div class="d-flex flex-wrap gap-2">' +
      '<button type="button" class="btn btn-brand btn-sm" id="helixStart">Allow camera &amp; calibrate</button>' +
      '<button type="button" class="btn btn-outline-navy btn-sm" id="helixSkip">Not now</button>' +
      '<a class="btn btn-outline-secondary btn-sm" href="' + (CFG.policyUrl || '/policy/attention') + '">Policy</a>' +
      '</div>' +
      '<div class="small text-muted mt-2 d-none" id="helixLiveWrap">' +
      '<span id="helixStatus">Starting…</span> · looking at <span id="helixHud">—</span>' +
      ' <button type="button" class="btn btn-link btn-sm p-0 ms-2" id="helixStop">Stop</button>' +
      '</div>' +
      '<div id="helixReview" class="small mt-2"></div>' +
      '</div>';
    document.body.appendChild(dock);

    var calib = document.createElement('div');
    calib.id = 'helixCalib';
    calib.className = 'd-none';
    calib.innerHTML =
      '<div class="helix-calib-inner">' +
      '<p>Click each mark. Sit still. Look with your eyes, not your head.</p>' +
      '<button type="button" class="helix-x" data-cal style="left:8%;top:10%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:50%;top:10%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:92%;top:10%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:8%;top:50%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:50%;top:50%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:92%;top:50%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:8%;top:88%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:50%;top:88%">✕</button>' +
      '<button type="button" class="helix-x" data-cal style="left:92%;top:88%">✕</button>' +
      '</div>';
    document.body.appendChild(calib);

    var dot = document.createElement('div');
    dot.id = 'helixGazeDot';
    document.body.appendChild(dot);

    var style = document.createElement('style');
    style.textContent =
      '#helixDock{position:fixed;right:1rem;bottom:1rem;z-index:1900;width:min(22rem,calc(100vw - 1.5rem))}' +
      '.helix-dock-card{background:var(--surface,#fff);color:var(--ink,#0a1628);border:1px solid rgba(12,28,48,.18);border-radius:.75rem;padding:.85rem 1rem;box-shadow:0 12px 32px rgba(0,0,0,.18)}' +
      '.helix-dock-top{display:flex;justify-content:space-between;align-items:center;gap:.5rem;margin-bottom:.35rem}' +
      '.helix-pill{font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;background:#f0c14b;color:#0a1628;border-radius:999px;padding:.15rem .5rem;font-weight:700}' +
      '.helix-copy{font-size:.82rem;color:var(--ink-muted,#4a5568);margin-bottom:.6rem}' +
      '#helixCalib{position:fixed;inset:0;z-index:2100;background:rgba(6,16,31,.72)}' +
      '.helix-calib-inner{position:relative;width:100%;height:100%;color:#fff;padding:1rem}' +
      '.helix-x{position:absolute;transform:translate(-50%,-50%);width:2.2rem;height:2.2rem;border-radius:50%;border:2px solid #f0c14b;background:#0a1628;color:#f0c14b;font-weight:700}' +
      '.helix-x.saved{background:#f0c14b;color:#0a1628}' +
      '#helixGazeDot{position:fixed;width:10px;height:10px;border-radius:50%;background:#f0c14b;pointer-events:none;z-index:2090;display:none;transform:translate(-50%,-50%);box-shadow:0 0 0 3px rgba(240,193,75,.35)}';
    document.head.appendChild(style);
  }

  function loadReview() {
    if (!CFG.summaryUrl) return;
    fetch(CFG.summaryUrl, { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var box = $('helixReview');
        if (!box) return;
        var review = (data && data.review) || [];
        if (!review.length) {
          box.textContent = '';
          return;
        }
        box.innerHTML = '<div class="fw-semibold">Thin dwell on this lesson (signal, not a score)</div>' +
          review.slice(0, 5).map(function (r) {
            return '<div>' + (r.heading || r.aoi_label) + ' · ' + (r.seconds || Math.round((r.dwell_ms || 0) / 1000)) + 's</div>';
          }).join('');
      }).catch(function () {});
  }

  function beginSession() {
    tagAois();
    var live = $('helixLiveWrap');
    if (live) live.classList.remove('d-none');
    var st = $('helixStatus');
    if (st) st.textContent = 'Requesting camera…';
    return postJSON(CFG.startUrl, {
      lesson_id: CFG.lessonId,
      section_id: CFG.sectionId,
      engine: 'webgazer',
      consent_version: POLICY_VERSION,
      viewport_w: window.innerWidth,
      viewport_h: window.innerHeight
    }).then(function (res) {
      if (!res || !res.session_id) throw new Error('session refused');
      sessionId = res.session_id;
      startedAt = now();
      return startEngine();
    }).then(function () {
      running = true;
      showCalib();
      flushTimer = setInterval(function () { flush(false); }, 4000);
    }).catch(function (err) {
      if (st) st.textContent = 'Camera unavailable — ' + (err.message || err);
    });
  }

  function stopSession() {
    running = false;
    calibrated = false;
    if (flushTimer) clearInterval(flushTimer);
    var dot = $('helixGazeDot');
    if (dot) dot.style.display = 'none';
    try { if (window.webgazer && webgazer.end) webgazer.end(); } catch (e) {}
    flush(true).then(loadReview);
    var st = $('helixStatus');
    if (st) st.textContent = 'Stopped';
  }

  function init() {
    buildChrome();
    tagAois();
    loadReview();
    var startBtn = $('helixStart');
    var skipBtn = $('helixSkip');
    var stopBtn = $('helixStop');
    if (startBtn) startBtn.onclick = function () {
      try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
      beginSession();
    };
    if (skipBtn) skipBtn.onclick = function () {
      var dock = $('helixDock');
      if (dock) dock.style.display = 'none';
    };
    if (stopBtn) stopBtn.onclick = stopSession;
    window.addEventListener('pagehide', function () { if (running) stopSession(); });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden && running) flush(false);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
