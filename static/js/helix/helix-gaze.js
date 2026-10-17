/* CIWT Helix runtime — opt-in attention signal for lesson pages.
   Camera mode: WebGazer (in-browser; video never leaves the device) with
   9-point calibration, 5-point validation (accuracy score), median/Kalman
   smoothing, face-lost / tab-hidden / low-confidence states, AOI timelines,
   heat grid, sequenced + retried + beacon uploads.
   Passive mode (phones, no camera, or student choice): reading-line AOI from
   scroll position + visibility + interaction. Never a grade.
   Requires helix-core.js (window.HelixCore) loaded first. */
(function () {
  'use strict';
  var CFG = window.HELIX || {};
  var Core = window.HelixCore;
  if (!CFG.lessonId || !Core) return;

  var TICK_MS = 250, BATCH_MS = 5000, FACE_LOST_MS = 1200, LOW_CONF = 0.25;
  var HIDDEN_END_MS = 15 * 60 * 1000, IDLE_MS = 45000, DRIFT_CHECK_MS = 12 * 60 * 1000;
  var DISMISS_KEY = 'ciwt-helix-dismissed', DOT_KEY = 'ciwt-helix-dot';
  var CAL_POINTS = [[10, 10], [50, 10], [90, 10], [10, 50], [50, 50], [90, 50], [10, 90], [50, 90], [90, 90]];
  var CAL_CLICKS = 5;
  var VAL_POINTS = [[50, 50], [18, 20], [82, 20], [18, 80], [82, 80]];

  var S = {
    server: null, mode: null, sessionId: null, phase: 'idle', t0: 0,
    filter: null, debounce: null, timeline: null, heat: null, queue: null,
    tick: null, batchTimer: null, lastSample: 0, lastFaceOk: 0, lowSince: 0,
    lastInteraction: Date.now(), hiddenAt: 0, paused: false, calibration: null,
    calAttempts: 0, lastCalibratedAt: 0, layoutDirty: true, samples: 0,
    aoiList: [], body: null, lastHit: null, conf: 0, faceLostSince: 0, warnedFace: false,
    uuid: null, showDot: false
  };

  function $(id) { return document.getElementById(id); }
  function now() { return Date.now(); }
  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function url(tpl, id) { return String(tpl).replace('/0/', '/' + id + '/'); }
  function uuid() { return 'hx-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10); }
  function store() { try { return window.localStorage; } catch (e) { return null; } }
  function device() {
    var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    var small = Math.min(screen.width, screen.height) < 600 || window.innerWidth < 600;
    if (coarse && small) return 'mobile';
    if (coarse) return 'tablet';
    return 'desktop';
  }
  function cameraPossible() {
    return !!(window.isSecureContext !== false && navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }
  function postJSON(u, body) {
    return fetch(u, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(body || {})
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) { j._status = r.status; return j; });
    });
  }

  /* ------------------------------------------------------------ AOIs */
  function slug(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'block'; }
  var SUB_KINDS = [['pre', 'code', 'Code'], ['table', 'table', 'Table'], ['figure,img', 'figure', 'Figure'],
                   ['.analogy-box,.callout,.alert,blockquote', 'callout', 'Callout']];
  function tagAois() {
    var body = S.body = $('lessonBody');
    var list = [];
    if (!body) return list;
    var order = 0;
    var heads = Array.prototype.slice.call(body.querySelectorAll('h2,h3,h4'));
    function mark(node, key, label, kind, ord) {
      node.setAttribute('data-aoi', key); node.setAttribute('data-aoi-label', label);
      node.setAttribute('data-aoi-order', String(ord)); node.setAttribute('data-aoi-kind', kind);
    }
    heads.forEach(function (h, i) {
      var label = (h.textContent || '').replace(/\s+/g, ' ').trim();
      if (!label) return;
      var key = 'h' + i + '-' + slug(label);
      var ord = order++;
      mark(h, key, label, 'heading', ord);
      var group = [h];
      var n = h.nextElementSibling;
      while (n && !/^H[2-4]$/.test(n.tagName)) { mark(n, key, label, 'heading', ord); group.push(n); n = n.nextElementSibling; }
      list.push({ key: key, label: label, order: ord, kind: 'heading', nodes: group });
      // sub-AOIs for code/tables/figures/callouts inside this block
      group.forEach(function (g) {
        SUB_KINDS.forEach(function (sk) {
          var found = g.matches && g.matches(sk[0]) ? [g] : Array.prototype.slice.call(g.querySelectorAll ? g.querySelectorAll(sk[0]) : []);
          found.forEach(function (f, j) {
            if (f.getAttribute('data-aoi-kind') && f.getAttribute('data-aoi-kind') !== 'heading') return;
            var sub = key + '~' + sk[1] + j;
            var slabel = label + ' \u203a ' + sk[2];
            var sord = order++;
            mark(f, sub, slabel, sk[1], sord);
            list.push({ key: sub, label: slabel, order: sord, kind: sk[1], nodes: [f] });
          });
        });
      });
    });
    if (!list.length) {
      mark(body, 'lesson-body', 'Lesson body', 'heading', 0);
      list.push({ key: 'lesson-body', label: 'Lesson body', order: 0, kind: 'heading', nodes: [body] });
    }
    var lab = $('chapter-lab');
    if (lab) { mark(lab, 'lesson-lab', 'Hands-on lab', 'lab', 900); list.push({ key: 'lesson-lab', label: 'Hands-on lab', order: 900, kind: 'lab', nodes: [lab] }); }
    S.aoiList = list;
    S.layoutDirty = true;
    return list;
  }
  function computeLayout() {
    var body = S.body;
    if (!body) return [];
    var br = body.getBoundingClientRect();
    if (!br.height) return [];
    return S.aoiList.filter(function (a) { return a.kind !== 'lab'; }).map(function (a) {
      var top = Infinity, bot = -Infinity;
      a.nodes.forEach(function (n) { var r = n.getBoundingClientRect(); top = Math.min(top, r.top); bot = Math.max(bot, r.bottom); });
      return { key: a.key, label: a.label, order: a.order, kind: a.kind,
               y0: Math.max(0, (top - br.top) / br.height), y1: Math.min(1, (bot - br.top) / br.height) };
    });
  }
  var OFF = { key: 'off_page', label: 'Looking away from page', order: 999, kind: 'state' };
  var CHROME = { key: 'chrome', label: 'Page chrome / navigation', order: 998, kind: 'state' };
  function hitAoi(x, y) {
    if (x == null || y == null || x < 0 || y < 0 || x > window.innerWidth || y > window.innerHeight) return OFF;
    var dock = $('helixDock');
    var node = document.elementFromPoint(x, y);
    if (node && dock && dock.contains(node)) return CHROME;
    while (node && node.getAttribute && !node.getAttribute('data-aoi')) node = node.parentElement;
    if (node && node.getAttribute) {
      return { key: node.getAttribute('data-aoi'), label: node.getAttribute('data-aoi-label'),
               order: parseInt(node.getAttribute('data-aoi-order') || '0', 10) || 0, kind: node.getAttribute('data-aoi-kind') || 'heading' };
    }
    return CHROME;
  }
  var STATES = {
    _hidden: { key: '_hidden', label: 'Tab hidden / app switched', order: 997, kind: 'state' },
    _face_lost: { key: '_face_lost', label: 'Face not detected', order: 996, kind: 'state' },
    _low_conf: { key: '_low_conf', label: 'Low-confidence estimate', order: 995, kind: 'state' },
    _idle: { key: '_idle', label: 'No activity (passive mode)', order: 994, kind: 'state' },
    _paused: { key: '_paused', label: 'Paused by student', order: 993, kind: 'state' }
  };

  /* ------------------------------------------------------------ dock UI */
  function buildDock() {
    if ($('helixDock')) return;
    var dock = el('section', { id: 'helixDock', 'class': 'helix-dock', 'aria-label': 'Helix attention signal', 'data-phase': 'idle' });
    dock.innerHTML =
      '<button type="button" class="helix-pill-btn" id="hxPill" aria-expanded="false" aria-controls="hxCard">' +
        '<span class="hx-dot" aria-hidden="true"></span><span class="hx-pill-text">Helix</span><span class="visually-hidden"> attention signal — open panel</span></button>' +
      '<div class="helix-card" id="hxCard" hidden>' +
        '<div class="hx-head"><strong><i class="bi bi-eye" aria-hidden="true"></i> Helix attention</strong>' +
          '<span class="hx-badge">Not a grade</span>' +
          '<button type="button" class="hx-icon-btn" id="hxMin" aria-label="Minimise Helix panel"><i class="bi bi-dash-lg" aria-hidden="true"></i></button></div>' +
        '<div id="hxBody"></div>' +
        '<p class="hx-status" id="hxStatus" role="status" aria-live="polite"></p>' +
      '</div>';
    document.body.appendChild(dock);
    $('hxPill').addEventListener('click', function () { setOpen(true); });
    $('hxMin').addEventListener('click', function () { setOpen(false); });
    var dot = el('div', { id: 'helixGazeDot', 'aria-hidden': 'true' });
    document.body.appendChild(dot);
    var toast = el('div', { id: 'hxToast', 'class': 'helix-toast', role: 'alert', hidden: '' });
    document.body.appendChild(toast);
  }
  function setOpen(open) {
    var card = $('hxCard'), pill = $('hxPill');
    if (!card) return;
    card.hidden = !open;
    pill.hidden = open;
    pill.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { var f = card.querySelector('button, a, input'); if (f) f.focus({ preventScroll: true }); }
  }
  function setPhase(p, pillText) {
    S.phase = p;
    var dock = $('helixDock');
    if (dock) dock.setAttribute('data-phase', p);
    var t = document.querySelector('#hxPill .hx-pill-text');
    if (t) t.textContent = pillText || 'Helix';
  }
  function status(msg) { var n = $('hxStatus'); if (n) n.textContent = msg || ''; }
  function body(html) { var n = $('hxBody'); if (n) n.innerHTML = html; return n; }
  function on(id, fn) { var n = $(id); if (n) n.addEventListener('click', fn); }
  function toast(html, actions, ms) {
    var t = $('hxToast');
    if (!t) return;
    t.innerHTML = '<div>' + html + '</div><div class="hx-toast-actions"></div>';
    var box = t.querySelector('.hx-toast-actions');
    (actions || []).concat([{ label: 'Dismiss', cls: 'btn-link', fn: function () {} }]).forEach(function (a) {
      var b = el('button', { type: 'button', 'class': 'btn btn-sm ' + (a.cls || 'btn-brand') }, esc(a.label));
      b.addEventListener('click', function () { t.hidden = true; a.fn(); });
      box.appendChild(b);
    });
    t.hidden = false;
    clearTimeout(t._h);
    if (ms) t._h = setTimeout(function () { t.hidden = true; }, ms);
  }

  function renderOffer() {
    setPhase('idle');
    var dev = device(), srv = S.server;
    var camOk = cameraPossible() && dev !== 'mobile';
    var passiveOk = srv.passive_enabled;
    var html = '<p class="hx-copy">Optional signal of which parts of this lesson you spend time on. Your instructor uses it to decide what to reteach — never as a score, attendance mark, or test condition.</p>';
    html += '<div class="hx-actions">';
    if (camOk) html += '<button type="button" class="btn btn-brand btn-sm" id="hxCam"><i class="bi bi-camera-video" aria-hidden="true"></i> Camera gaze</button>';
    if (passiveOk) html += '<button type="button" class="btn ' + (camOk ? 'btn-outline-navy' : 'btn-brand') + ' btn-sm" id="hxPassive"><i class="bi bi-phone" aria-hidden="true"></i> Reading signal (no camera)</button>';
    html += '<button type="button" class="btn btn-outline-secondary btn-sm" id="hxSkip">Not now</button></div>';
    if (!camOk && dev === 'mobile') html += '<p class="hx-note">On phones Helix uses scroll position and screen visibility instead of the camera — gaze estimation is not reliable on small screens.</p>';
    else if (!cameraPossible()) html += '<p class="hx-note">Camera gaze needs HTTPS and camera access, so only the reading signal is available here.</p>';
    if (dev === 'tablet' && camOk) html += '<p class="hx-note">Tablet: prop it up at eye level for camera gaze, or use the reading signal.</p>';
    html += '<p class="hx-links"><a href="' + esc(CFG.policyUrl) + '">How Helix works</a> · <a href="' + esc(CFG.myDataUrl) + '">My data</a></p>';
    body(html);
    on('hxCam', function () { ensureConsent('gaze'); });
    on('hxPassive', function () { ensureConsent('passive'); });
    on('hxSkip', function () {
      var st = store(); if (st) st.setItem(DISMISS_KEY, String(now()));
      setOpen(false); setPhase('idle', 'Helix off');
    });
    status('');
  }

  function ensureConsent(mode) {
    var c = S.server.consent;
    if (c.granted && ((mode === 'gaze' && c.camera_ok) || (mode === 'passive' && c.passive_ok))) return start(mode);
    setPhase('consent');
    body(
      '<form id="hxConsent" class="hx-consent">' +
      (c.stale ? '<p class="hx-note"><strong>The policy changed</strong> since you last agreed. Please review it again.</p>' : '') +
      '<p class="hx-copy">Before Helix records anything:</p><ul class="hx-list">' +
      '<li>Camera video is processed <strong>only in this browser</strong>. No images are uploaded.</li>' +
      '<li>Stored: which lesson blocks you spent time on, for how long, and data-quality info (calibration accuracy, face/tab states).</li>' +
      '<li>It is <strong>not a grade</strong> and not required for any quiz or test.</li>' +
      '<li>You can stop any time, withdraw consent, and delete your data from <a href="' + esc(CFG.myDataUrl) + '">My attention data</a>.</li></ul>' +
      '<div class="form-check"><input class="form-check-input" type="checkbox" id="hxAgree" required>' +
      '<label class="form-check-label" for="hxAgree">I have read the <a href="' + esc(CFG.policyUrl) + '" target="_blank" rel="noopener">attention policy</a> (v' + esc(S.server.policy_version) + ') and agree to take part.</label></div>' +
      '<div class="form-check"><input class="form-check-input" type="checkbox" id="hxCamOk" ' + (mode === 'gaze' ? 'checked' : '') + '>' +
      '<label class="form-check-label" for="hxCamOk">Allow camera gaze estimation</label></div>' +
      '<div class="form-check"><input class="form-check-input" type="checkbox" id="hxPassOk" checked>' +
      '<label class="form-check-label" for="hxPassOk">Allow the no-camera reading signal</label></div>' +
      '<div class="hx-actions mt-2"><button type="submit" class="btn btn-brand btn-sm">Agree and continue</button>' +
      '<button type="button" class="btn btn-outline-secondary btn-sm" id="hxBack">Back</button></div></form>');
    on('hxBack', renderOffer);
    $('hxConsent').addEventListener('submit', function (e) {
      e.preventDefault();
      if (!$('hxAgree').checked) { status('Tick the agreement box to continue.'); return; }
      var cam = $('hxCamOk').checked, pas = $('hxPassOk').checked;
      if ((mode === 'gaze' && !cam) || (mode === 'passive' && !pas)) mode = cam ? 'gaze' : (pas ? 'passive' : null);
      if (!mode) { status('Choose at least one signal type.'); return; }
      status('Saving consent…');
      postJSON(CFG.consentApiUrl, { agree: true, camera_ok: cam, passive_ok: pas }).then(function (r) {
        if (!r.ok) { status('Could not save consent (' + (r.error || r._status) + ').'); return; }
        S.server.consent = { granted: true, camera_ok: cam, passive_ok: pas };
        start(mode);
      }).catch(function () { status('Network error — consent not saved.'); });
    });
  }

  /* ------------------------------------------------------------ session lifecycle */
  function start(mode) {
    S.mode = mode;
    S.uuid = uuid();
    tagAois();
    status(mode === 'gaze' ? 'Starting camera session…' : 'Starting reading signal…');
    var w = window.innerWidth, h = window.innerHeight;
    return postJSON(CFG.startUrl, {
      lesson_id: CFG.lessonId, section_id: CFG.sectionId, mode: mode, device: device(),
      client_uuid: S.uuid, consent_version: S.server.policy_version, viewport_w: w, viewport_h: h
    }).then(function (res) {
      if (!res || !res.session_id) {
        var why = { consent_required: 'consent needed', not_enrolled: 'you are not enrolled in this class', disabled_for_section: 'turned off for this class' }[res && res.error] || (res && res.error) || 'refused';
        throw new Error(why);
      }
      S.sessionId = res.session_id;
      S.filter = new Core.GazeFilter({ bounds: { w: w, h: h } });
      S.debounce = new Core.AoiDebouncer(mode === 'gaze' ? 160 : 400);
      S.heat = new Core.HeatGrid(20, 60);
      S.queue = new Core.BatchQueue({
        storage: store(), key: 'helix-q-' + S.sessionId, send: sendBatch(S.sessionId),
        onState: function (st) { if (!st.ok) status('Upload retrying in ' + Math.round(st.retryIn / 1000) + 's (' + st.pending + ' queued)'); }
      });
      if (mode === 'gaze') return startCamera();
      return startPassive();
    }).catch(function (err) {
      setPhase('error');
      body('<p class="hx-copy">Helix could not start: ' + esc(err.message || err) + '.</p>' +
        '<div class="hx-actions">' + (S.server.passive_enabled && mode === 'gaze' ? '<button type="button" class="btn btn-brand btn-sm" id="hxFallback">Use reading signal instead</button>' : '') +
        '<button type="button" class="btn btn-outline-secondary btn-sm" id="hxBack">Back</button></div>');
      on('hxFallback', function () { endSession(true).then(function () { ensureConsent('passive'); }); });
      on('hxBack', function () { endSession(true).then(renderOffer); });
      status('');
    });
  }

  function sendBatch(sid) {
    return function (batch) {
      return fetch(url(CFG.batchUrl, sid), {
        method: 'POST', credentials: 'same-origin', keepalive: true,
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(batch)
      }).then(function (r) {
        if (r.status >= 400 && r.status < 500) {
          // not retryable (session deleted, consent revoked, logged out): drop it
          if (sid === S.sessionId && r.status !== 401) hardStop('The server stopped this session (' + r.status + ').');
          return { ok: true, dropped: true };
        }
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      });
    };
  }

  function beginLive() {
    S.t0 = now();
    S.timeline = new Core.StateTimeline(S.t0);
    S.lastSample = S.lastFaceOk = now();
    clearInterval(S.tick); clearInterval(S.batchTimer);
    S.tick = setInterval(tick, TICK_MS);
    S.batchTimer = setInterval(function () { queueBatch(false); S.queue.flush(); }, BATCH_MS);
    renderLive();
  }

  function queueBatch(end) {
    if (!S.timeline || !S.queue) return;
    var snap = S.timeline.checkpoint(now());
    var batch = {
      segments: snap.segments.slice(0, 250), buckets: snap.buckets, totals: snap.totals,
      heat: S.heat.toJSON(), sample_count: S.samples, rejected: S.filter ? S.filter.rejected : 0,
      viewport_w: window.innerWidth, viewport_h: window.innerHeight, end: !!end
    };
    if (S.layoutDirty) { batch.layout = computeLayout(); S.layoutDirty = false; }
    S.queue.push(batch);
  }

  function tick() {
    var t = now();
    var state;
    if (S.paused) state = STATES._paused;
    else if (document.hidden) state = STATES._hidden;
    else if (S.mode === 'gaze') {
      if (t - S.lastFaceOk > FACE_LOST_MS || t - S.lastSample > FACE_LOST_MS + 300) {
        state = STATES._face_lost;
        if (!S.faceLostSince) S.faceLostSince = t;
        if (t - S.faceLostSince > 8000 && !S.warnedFace) {
          S.warnedFace = true;
          toast('<strong>Helix can\u2019t see your face.</strong> Check lighting and that the camera is not covered.', [{ label: 'Pause Helix', fn: togglePause }], 12000);
        }
      } else {
        S.faceLostSince = 0; S.warnedFace = false;
        var c = Core.confidence({ face: true, dispersion: S.filter.dispersion(), diag: Math.hypot(innerWidth, innerHeight),
                                  calibrationScore: S.calibration ? S.calibration.score : null, sinceSampleMs: t - S.lastSample });
        S.conf = c;
        if (c < LOW_CONF) { if (!S.lowSince) S.lowSince = t; } else S.lowSince = 0;
        state = (S.lowSince && t - S.lowSince > 1500) ? STATES._low_conf : (S.lastHit || OFF);
      }
      if (S.lastCalibratedAt && t - S.lastCalibratedAt > DRIFT_CHECK_MS && !S.driftPrompted) {
        S.driftPrompted = true;
        toast('It has been a while since calibration — accuracy drifts as you move. Recalibrate (about 30 seconds)?', [{ label: 'Recalibrate', fn: recalibrate }], 20000);
      }
      var tl = S.timeline && S.timeline.totals;
      if (tl && tl.total > 60000 && tl.low_conf / tl.total > 0.35 && !S.lowPrompted) {
        S.lowPrompted = true;
        toast('Helix is unsure where you are looking much of the time. A quick recalibration usually fixes this.', [{ label: 'Recalibrate', fn: recalibrate }, { label: 'Switch to reading signal', cls: 'btn-outline-navy', fn: switchToPassive }], 20000);
      }
    } else {
      if (t - S.lastInteraction > IDLE_MS) state = STATES._idle;
      else {
        var y = Math.round(window.innerHeight * 0.38);
        var br = S.body ? S.body.getBoundingClientRect() : null;
        var x = br ? Math.round(br.left + Math.min(br.width, window.innerWidth) / 2) : Math.round(innerWidth / 2);
        state = S.debounce.feed(hitAoi(x, y), t);
        if (br && br.height) {
          var fy = (y - br.top) / br.height;
          for (var cx = 3; cx < 15; cx++) S.heat.add((cx + 0.5) / 20, fy, TICK_MS / 12);
        }
      }
    }
    if (document.hidden) { if (!S.hiddenAt) S.hiddenAt = t; if (t - S.hiddenAt > HIDDEN_END_MS) { autoEnd('tab hidden for 15+ minutes'); return; } }
    else S.hiddenAt = 0;
    S.timeline.enter(state, t);
    if (S.phase === 'live' || S.phase === 'passive') updateLiveText(state);
  }

  var lastLiveText = '';
  function updateLiveText(state) {
    var txt = state.kind === 'state' ? state.label : 'Reading: ' + state.label;
    if (txt === lastLiveText) return;
    lastLiveText = txt;
    var n = $('hxNow'); if (n) n.textContent = txt;
    var dock = $('helixDock'); if (dock) dock.setAttribute('data-state', state.kind === 'state' ? state.key : 'reading');
  }

  function renderLive() {
    var passive = S.mode === 'passive';
    setPhase(passive ? 'passive' : 'live', passive ? 'Helix · reading' : 'Helix · live');
    var cal = S.calibration;
    var band = cal ? ('<span class="hx-acc hx-acc-' + cal.band + '">Accuracy ' + cal.score + '% · ' + cal.band + '</span>') : '<span class="hx-acc hx-acc-info">Reading signal · no camera</span>';
    body('<div class="hx-live">' + band + '<p class="hx-now" id="hxNow">Starting…</p></div>' +
      '<div class="hx-actions">' +
      '<button type="button" class="btn btn-outline-navy btn-sm" id="hxPause" aria-pressed="false"><i class="bi bi-pause-fill" aria-hidden="true"></i> Pause</button>' +
      (passive ? '' : '<button type="button" class="btn btn-outline-navy btn-sm" id="hxRecal"><i class="bi bi-bullseye" aria-hidden="true"></i> Recalibrate</button>') +
      (passive ? '' : '<button type="button" class="btn btn-outline-secondary btn-sm" id="hxDotBtn" aria-pressed="' + S.showDot + '">' + (S.showDot ? 'Hide' : 'Show') + ' gaze dot</button>') +
      '<button type="button" class="btn btn-danger btn-sm" id="hxStop"><i class="bi bi-stop-fill" aria-hidden="true"></i> Stop</button></div>' +
      '<p class="hx-note">' + (passive ? 'Uses which block sits on your reading line, screen visibility and recent scrolling/touch.' : 'Video stays in this browser. Look naturally; move your eyes more than your head.') + '</p>');
    on('hxPause', togglePause); on('hxRecal', recalibrate); on('hxStop', function () { stopSession(); });
    on('hxDotBtn', function () {
      S.showDot = !S.showDot; var st = store(); if (st) st.setItem(DOT_KEY, S.showDot ? '1' : '0');
      if (!S.showDot) $('helixGazeDot').style.display = 'none';
      renderLive();
    });
    status('');
  }

  function togglePause() {
    S.paused = !S.paused;
    try { if (S.mode === 'gaze' && window.webgazer) { if (S.paused) webgazer.pause(); else webgazer.resume(); } } catch (e) {}
    var b = $('hxPause');
    if (b) { b.setAttribute('aria-pressed', S.paused ? 'true' : 'false'); b.innerHTML = S.paused ? '<i class="bi bi-play-fill" aria-hidden="true"></i> Resume' : '<i class="bi bi-pause-fill" aria-hidden="true"></i> Pause'; }
    setPhase(S.paused ? 'paused' : (S.mode === 'passive' ? 'passive' : 'live'), S.paused ? 'Helix · paused' : null);
    if (S.paused) $('helixGazeDot').style.display = 'none';
    status(S.paused ? 'Paused — nothing is being measured.' : 'Resumed.');
  }

  function hardStop(msg) {
    teardown();
    setPhase('ended', 'Helix');
    body('<p class="hx-copy">' + esc(msg) + '</p><div class="hx-actions"><button type="button" class="btn btn-outline-navy btn-sm" id="hxAgain">Start again</button></div>');
    on('hxAgain', function () { boot(true); });
  }

  function teardown() {
    clearInterval(S.tick); clearInterval(S.batchTimer); S.tick = S.batchTimer = null;
    var dot = $('helixGazeDot'); if (dot) dot.style.display = 'none';
    try { if (window.webgazer && S.mode === 'gaze') { webgazer.clearGazeListener && webgazer.clearGazeListener(); webgazer.end(); } } catch (e) {}
    detachPassive();
    var cal = $('helixCalib'); if (cal) cal.remove();
  }

  function endSession(silent) {
    if (!S.sessionId) return Promise.resolve();
    var sid = S.sessionId;
    if (S.timeline) queueBatch(true);
    else if (S.queue) S.queue.push({ segments: [], buckets: [], end: true });
    teardown();
    S.sessionId = null;
    var q = S.queue;
    return (q ? q.flush() : Promise.resolve()).then(function () { return sid; }).catch(function () { return sid; });
  }

  function stopSession() {
    status('Saving…');
    return endSession().then(function () {
      setPhase('ended', 'Helix');
      body('<p class="hx-copy"><strong>Session saved.</strong> Thanks — this helps your instructor see which parts of the lesson need another pass.</p>' +
        '<div id="hxReview" class="hx-review"></div>' +
        '<div class="hx-actions"><button type="button" class="btn btn-outline-navy btn-sm" id="hxAgain">Start another session</button>' +
        '<a class="btn btn-outline-secondary btn-sm" href="' + esc(CFG.myDataUrl) + '">My data</a></div>');
      on('hxAgain', function () { boot(true); });
      status(S.queue && S.queue.items.length ? S.queue.items.length + ' upload(s) will retry automatically.' : '');
      loadReview();
    });
  }

  function autoEnd(reason) {
    endSession().then(function () {
      setPhase('ended', 'Helix');
      body('<p class="hx-copy">Helix ended the session automatically (' + esc(reason) + ').</p><div class="hx-actions"><button type="button" class="btn btn-brand btn-sm" id="hxAgain">Resume with a new session</button></div>');
      on('hxAgain', function () { boot(true); });
    });
  }

  function loadReview() {
    if (!CFG.summaryUrl) return;
    fetch(CFG.summaryUrl, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (data) {
      var box = $('hxReview');
      if (!box) return;
      var review = (data && data.review) || [];
      if (!review.length) { box.innerHTML = '<p class="hx-note">No thin spots across your sessions on this lesson.</p>'; return; }
      box.innerHTML = '<p class="hx-copy mb-1"><strong>Worth a second look</strong> (little time spent):</p><ul class="hx-list">' +
        review.slice(0, 5).map(function (r) {
          return '<li><a href="#" data-jump="' + esc(r.key || '') + '">' + esc(r.heading) + '</a> <span class="text-muted">· ' + r.seconds + 's</span></li>';
        }).join('') + '</ul>';
      box.querySelectorAll('[data-jump]').forEach(function (a) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          var t = document.querySelector('[data-aoi="' + a.getAttribute('data-jump').replace(/"/g, '') + '"]');
          if (t) { t.scrollIntoView({ behavior: 'smooth', block: 'start' }); t.classList.add('hx-flash'); setTimeout(function () { t.classList.remove('hx-flash'); }, 1800); }
        });
      });
    }).catch(function () {});
  }

  /* ------------------------------------------------------------ camera mode */
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.webgazer) return resolve();
      var s = document.createElement('script');
      s.src = src; s.async = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error('could not load the gaze engine')); };
      document.head.appendChild(s);
    });
  }

  function startCamera() {
    status('Loading gaze engine…');
    return loadScript(CFG.engineUrl).catch(function () { return loadScript(CFG.cdnUrl); }).then(function () {
      if (!window.webgazer) throw new Error('gaze engine missing');
      status('Waiting for camera permission…');
      webgazer.params.showVideo = true;
      webgazer.params.showFaceOverlay = true;
      webgazer.params.showFaceFeedbackBox = true;
      webgazer.params.showGazeDot = false;
      if (webgazer.saveDataAcrossSessions) webgazer.saveDataAcrossSessions(false);
      if (webgazer.applyKalmanFilter) webgazer.applyKalmanFilter(false); // we run our own median gate + Kalman
      if (webgazer.setRegression) { try { webgazer.setRegression('ridge'); } catch (e) {} }
      webgazer.setGazeListener(onGaze);
      return webgazer.begin(function onFail() { /* handled by rejection below */ });
    }).then(function () {
      if (webgazer.showPredictionPoints) webgazer.showPredictionPoints(false);
      pollFace();
      S.calAttempts = 0;
      return calibrate(false);
    }).catch(function (err) {
      var msg = String(err && (err.name || err.message) || err);
      if (/NotAllowed|Permission|denied/i.test(msg)) throw new Error('camera permission was denied');
      if (/NotFound|Overconstrained|DevicesNotFound/i.test(msg)) throw new Error('no camera was found');
      throw err;
    });
  }

  function pollFace() {
    clearInterval(S.facePoll);
    S.facePoll = setInterval(function () {
      if (!window.webgazer || !S.sessionId) { clearInterval(S.facePoll); return; }
      var ok = null;
      try {
        var tr = webgazer.getTracker && webgazer.getTracker();
        if (tr && tr.getPositions) { var pos = tr.getPositions(); ok = !!(pos && pos.length); }
      } catch (e) { ok = null; }
      if (ok === true || (ok === null && now() - S.lastSample < 600)) S.lastFaceOk = now();
    }, 400);
  }

  var calSink = null; // during validation, raw predictions are collected here
  function onGaze(data) {
    var t = now();
    if (!data) return; // no prediction: face lost handled by the ticker timeout
    var raw = { x: data.x, y: data.y };
    if (calSink) { var f0 = S.filter.push(raw.x, raw.y); if (f0.ok) calSink.push({ x: f0.x, y: f0.y }); return; }
    if (!S.timeline || S.paused || document.hidden) return;
    var dt = Math.min(200, t - S.lastSample);
    S.lastSample = t;
    S.samples++;
    var f = S.filter.push(raw.x, raw.y);
    if (!f.ok) return;
    S.lastHit = S.debounce.feed(hitAoi(f.x, f.y), t);
    if (S.body) {
      var br = S.body.getBoundingClientRect();
      if (br.width && br.height) S.heat.add((f.x - br.left) / br.width, (f.y - br.top) / br.height, dt);
    }
    if (S.showDot) { var dot = $('helixGazeDot'); dot.style.transform = 'translate(' + (f.x - 7) + 'px,' + (f.y - 7) + 'px)'; dot.style.display = 'block'; }
  }

  function calibrate(isRecal) {
    return new Promise(function (resolve) {
      setPhase('calibrating', 'Helix · calibrating');
      try { webgazer.showVideoPreview(true); webgazer.showFaceFeedbackBox && webgazer.showFaceFeedbackBox(true); } catch (e) {}
      try { webgazer.clearData && isRecal && S.calAttempts > 1 && webgazer.clearData(); } catch (e) {}
      var ov = el('div', { id: 'helixCalib', 'class': 'helix-calib', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'hxCalTitle' });
      ov.innerHTML = '<div class="hx-cal-help"><h2 id="hxCalTitle" class="h5">Calibrate Helix <span class="hx-cal-step">step 1 of 2</span></h2>' +
        '<p>Keep your head still and about an arm\u2019s length from the screen. <strong>Look at each dot and click it ' + CAL_CLICKS + ' times</strong> until it turns gold. ' +
        'Keyboard: Tab to a dot, press Space.</p><p class="small mb-0"><span id="hxCalCount">0</span> / ' + CAL_POINTS.length + ' dots · <button type="button" class="btn btn-link btn-sm p-0 text-reset" id="hxCalCancel">Cancel (Esc)</button></p></div>';
      CAL_POINTS.forEach(function (p, i) {
        var b = el('button', { type: 'button', 'class': 'hx-cal-pt', style: 'left:' + p[0] + '%;top:' + p[1] + '%', 'aria-label': 'Calibration dot ' + (i + 1) + ' of ' + CAL_POINTS.length, 'data-left': String(CAL_CLICKS) });
        b.innerHTML = '<span class="hx-ring" style="--p:0"></span>';
        ov.appendChild(b);
      });
      document.body.appendChild(ov);
      var done = 0;
      ov.querySelectorAll('.hx-cal-pt').forEach(function (b) {
        b.addEventListener('click', function (e) {
          var left = parseInt(b.getAttribute('data-left'), 10);
          if (left <= 0) return;
          var r = b.getBoundingClientRect();
          // pointer clicks are learned by WebGazer's own listener; keyboard "clicks" have no coordinates
          if (e.detail === 0 && webgazer.recordScreenPosition) { try { webgazer.recordScreenPosition(r.left + r.width / 2, r.top + r.height / 2, 'click'); } catch (x) {} }
          left -= 1;
          b.setAttribute('data-left', String(left));
          b.querySelector('.hx-ring').style.setProperty('--p', String((CAL_CLICKS - left) / CAL_CLICKS));
          if (left === 0) {
            b.classList.add('done'); b.setAttribute('aria-label', b.getAttribute('aria-label') + ' — done');
            done += 1; $('hxCalCount').textContent = String(done);
            if (done === CAL_POINTS.length) validate(ov, isRecal).then(resolve);
          }
        });
      });
      function cancel() { document.removeEventListener('keydown', esck); ov.remove(); endSession(true).then(renderOffer); resolve(); }
      function esck(e) { if (e.key === 'Escape') cancel(); }
      document.addEventListener('keydown', esck);
      ov._cleanup = function () { document.removeEventListener('keydown', esck); };
      $('hxCalCancel').addEventListener('click', cancel);
      ov.querySelector('.hx-cal-pt').focus();
    });
  }

  function validate(ov, isRecal) {
    ov.querySelectorAll('.hx-cal-pt').forEach(function (b) { b.remove(); });
    ov.querySelector('.hx-cal-help').innerHTML = '<h2 class="h5">Check accuracy <span class="hx-cal-step">step 2 of 2</span></h2><p>Now just <strong>look</strong> at each dot as it appears — no clicking. About 8 seconds.</p>';
    try { webgazer.showVideoPreview(false); } catch (e) {}
    var target = el('div', { 'class': 'hx-val-pt', 'aria-hidden': 'true' });
    ov.appendChild(target);
    var results = [];
    var w = window.innerWidth, h = window.innerHeight;
    S.filter = new Core.GazeFilter({ bounds: { w: w, h: h } });
    return VAL_POINTS.reduce(function (p, pt) {
      return p.then(function () {
        return new Promise(function (res) {
          var x = pt[0] / 100 * w, y = pt[1] / 100 * h;
          target.style.left = x + 'px'; target.style.top = y + 'px';
          target.classList.remove('pulse'); void target.offsetWidth; target.classList.add('pulse');
          var samples = [];
          setTimeout(function () { calSink = samples; }, 550);
          setTimeout(function () { calSink = null; results.push({ x: x, y: y, samples: samples }); res(); }, 1650);
        });
      });
    }, Promise.resolve()).then(function () {
      var score = Core.scoreValidation(results, { w: w, h: h });
      S.calAttempts += 1;
      S.calibration = score;
      postJSON(url(CFG.calibratedUrl, S.sessionId), {
        calibration_points: CAL_POINTS.length, calibration_score: score.score,
        validation_error_px: score.errorPx, validation_precision_px: score.precisionPx, recalibration: !!isRecal
      }).catch(function () {});
      return showValidation(ov, score, results, isRecal);
    });
  }

  function showValidation(ov, score, results, isRecal) {
    return new Promise(function (resolve) {
      var min = S.server.min_accuracy || 45;
      var ok = score.score >= min;
      var tips = '<ul class="small text-start mb-2"><li>Face a light source; avoid a bright window behind you.</li><li>Keep your face centred in the camera box.</li><li>Look at the dot centre and keep your head still while clicking.</li></ul>';
      var marks = results.map(function (r) {
        var s = r.samples, n = s.length;
        if (!n) return '';
        var cx = s.reduce(function (a, q) { return a + q.x; }, 0) / n, cy = s.reduce(function (a, q) { return a + q.y; }, 0) / n;
        return '<span class="hx-val-target" style="left:' + r.x + 'px;top:' + r.y + 'px"></span><span class="hx-val-est" style="left:' + cx + 'px;top:' + cy + 'px"></span>';
      }).join('');
      ov.querySelectorAll('.hx-val-pt').forEach(function (n) { n.remove(); });
      ov.insertAdjacentHTML('beforeend', marks);
      ov.querySelector('.hx-cal-help').innerHTML =
        '<h2 class="h5">Accuracy: ' + score.score + '% <span class="hx-acc hx-acc-' + score.band + '">' + score.band + '</span></h2>' +
        '<p class="mb-2">Average error \u2248 ' + score.errorPx + ' px (rings = targets, dots = Helix estimate).</p>' +
        (ok ? '<p class="mb-2">Good enough for heading-level areas of interest.</p>' : '<p class="mb-2"><strong>Below the class threshold (' + min + '%).</strong> Recalibrating usually helps:</p>' + tips) +
        '<div class="d-flex flex-wrap gap-2 justify-content-center">' +
        (ok ? '<button type="button" class="btn btn-brand" id="hxGo">Start reading</button>' : '') +
        '<button type="button" class="btn ' + (ok ? 'btn-outline-light' : 'btn-brand') + '" id="hxRetry">Recalibrate</button>' +
        (!ok && S.calAttempts >= 2 && S.server.passive_enabled ? '<button type="button" class="btn btn-outline-light" id="hxToPassive">Use reading signal instead</button>' : '') +
        (!ok ? '<button type="button" class="btn btn-outline-light" id="hxGoAnyway">Continue anyway</button>' : '') +
        '</div>';
      function finish() { if (ov._cleanup) ov._cleanup(); ov.remove(); S.lastCalibratedAt = now(); S.driftPrompted = false; S.lowPrompted = false; S.filter = new Core.GazeFilter({ bounds: { w: innerWidth, h: innerHeight } }); }
      on('hxGo', function () { finish(); if (isRecal) { S.paused = false; renderLive(); } else beginLive(); resolve(); });
      on('hxGoAnyway', function () { finish(); if (isRecal) { S.paused = false; renderLive(); } else beginLive(); resolve(); });
      on('hxRetry', function () { if (ov._cleanup) ov._cleanup(); ov.remove(); calibrate(isRecal).then(resolve); });
      on('hxToPassive', function () { if (ov._cleanup) ov._cleanup(); ov.remove(); switchToPassive(); resolve(); });
      var first = ov.querySelector('.btn'); if (first) first.focus();
    });
  }

  function recalibrate() {
    if (S.mode !== 'gaze' || !window.webgazer) return;
    S.paused = true; // calibration time is recorded as paused, not reading
    calibrate(true);
  }

  function switchToPassive() {
    endSession(true).then(function () {
      if (S.server.consent.passive_ok) start('passive'); else ensureConsent('passive');
    });
  }

  /* ------------------------------------------------------------ passive mode */
  var passiveHandlers = null;
  function startPassive() {
    var bump = function () { S.lastInteraction = now(); };
    passiveHandlers = bump;
    ['scroll', 'touchstart', 'touchmove', 'keydown', 'mousemove', 'wheel', 'pointerdown'].forEach(function (ev) {
      window.addEventListener(ev, bump, { passive: true });
    });
    S.lastInteraction = now();
    S.calibration = null;
    beginLive();
    return Promise.resolve();
  }
  function detachPassive() {
    if (!passiveHandlers) return;
    ['scroll', 'touchstart', 'touchmove', 'keydown', 'mousemove', 'wheel', 'pointerdown'].forEach(function (ev) {
      window.removeEventListener(ev, passiveHandlers);
    });
    passiveHandlers = null;
  }

  /* ------------------------------------------------------------ page lifecycle */
  function beaconAll(q, sid) {
    if (!q || !navigator.sendBeacon) return;
    var left = [];
    q.items.forEach(function (b) {
      var ok = false;
      try { ok = navigator.sendBeacon(url(CFG.batchUrl, sid), new Blob([JSON.stringify(b)], { type: 'application/json' })); } catch (e) {}
      if (!ok) left.push(b);
    });
    q.items = left; q._save();
  }
  function onPageHide() {
    if (!S.sessionId || !S.timeline) return;
    queueBatch(true);
    beaconAll(S.queue, S.sessionId);
    teardown();
    S.sessionId = null;
  }
  function flushLeftovers() {
    // uploads queued by a tab that crashed / lost network before it could send
    var st = store();
    if (!st) return;
    for (var i = st.length - 1; i >= 0; i--) {
      var k = st.key(i);
      var m = k && /^helix-q-(\d+)$/.exec(k);
      if (!m || (S.sessionId && +m[1] === S.sessionId)) continue;
      (function (sid, key) {
        var q = new Core.BatchQueue({ storage: st, key: key, send: sendBatch(sid) });
        q.flush();
      })(+m[1], k);
    }
  }

  function boot(open) {
    fetch(CFG.configUrl, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (cfg) {
      S.server = cfg;
      if (!cfg.enabled || !cfg.can_record) return; // Helix off for this class: render nothing
      buildDock();
      var st = store();
      S.showDot = !!(st && st.getItem(DOT_KEY) === '1');
      renderOffer();
      var dismissed = st && +st.getItem(DISMISS_KEY) > now() - 7 * 864e5;
      if (dismissed && !open) setPhase('idle', 'Helix off');
      setOpen(!!open || (!dismissed && window.innerWidth >= 992));
      flushLeftovers();
    }).catch(function () { /* Helix is optional: fail silently */ });
  }

  window.addEventListener('pagehide', onPageHide);
  window.addEventListener('pageshow', function (e) { if (e.persisted && !S.sessionId && S.server) renderOffer(); });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden && S.queue && S.timeline) { queueBatch(false); S.queue.flush(); }
  });
  var resizeT;
  window.addEventListener('resize', function () {
    clearTimeout(resizeT);
    resizeT = setTimeout(function () { S.layoutDirty = true; if (S.filter) S.filter.bounds = { w: innerWidth, h: innerHeight }; }, 300);
  });
  window.HelixRuntime = { state: S, tagAois: tagAois, computeLayout: computeLayout, hitAoi: hitAoi, stop: stopSession };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { boot(false); });
  else boot(false);
})();
