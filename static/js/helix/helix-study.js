/* Helix accuracy study (pass 10). Two rounds on the participant's own device with a balanced,
   server-assigned arm (calibration method x camera resolution). Only the numeric validation result
   is posted (window.HelixStudy.payload): no frames, landmarks or gaze samples. */
(function () {
  'use strict';
  var E = window.HelixEngine, Calib = window.HelixCalib, CFG = window.HELIX_STUDY, ENG = window.HELIX_ENGINE || {};
  var $ = function (id) { return document.getElementById(id); };
  var pair = 'p' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8), round = 0, engine = null, results = [];
  function csrf() { var m = document.querySelector('meta[name="csrf-token"]'); return m ? m.content : ''; }
  function state(t) { $('hxStudyState').textContent = t; }
  function device() {   // same rule as the lesson runtime (helix-gaze.js)
    var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    var small = Math.min(screen.width, screen.height) < 600 || window.innerWidth < 600;
    return coarse && small ? 'mobile' : coarse ? 'tablet' : 'desktop';
  }
  function browserTag() {   // family + major version only (same as helix-gaze.js)
    var ua = navigator.userAgent || '', m;
    if ((m = /Edg\/(\d+)/.exec(ua))) return 'Edge ' + m[1];
    if ((m = /OPR\/(\d+)/.exec(ua))) return 'Opera ' + m[1];
    if ((m = /SamsungBrowser\/(\d+)/.exec(ua))) return 'Samsung ' + m[1];
    if ((m = /Firefox\/(\d+)/.exec(ua)) || (m = /FxiOS\/(\d+)/.exec(ua))) return 'Firefox ' + m[1];
    if ((m = /CriOS\/(\d+)/.exec(ua))) return 'Chrome iOS ' + m[1];
    if ((m = /Chrome\/(\d+)/.exec(ua))) return 'Chrome ' + m[1];
    if ((m = /Version\/(\d+).*Safari/.exec(ua))) return 'Safari ' + m[1];
    return 'Other';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function label(a) { return (a.method === 'follow' ? 'follow the dot' : 'dots') + (a.hires ? ', 1080p camera' : ''); }

  function nextArm() {
    var capable = E && E.hiResCapable ? (function () { var keep = ENG.hiRes; ENG.hiRes = true; var c = E.hiResCapable(device() === 'mobile'); ENG.hiRes = keep; return c; })() : false;
    return fetch(CFG.armUrl + '?device=' + device() + '&hires_capable=' + (capable ? 1 : 0) + '&pair=' + pair, { credentials: 'same-origin' })
      .then(function (r) { return r.json(); });
  }
  function stopEngine() { if (engine) { try { engine.stop(); } catch (e) { /* ignore */ } engine = null; } }

  function runRound() {
    $('hxStudyStart').disabled = true; state('Assigning round ' + (round + 1) + '\u2026');
    var arm;
    return nextArm().then(function (a) {
      if (!a.ok || a.done) { finish(); return null; }
      arm = a; stopEngine();
      ENG.hiRes = !!a.hires;                      // read by the engine when the camera starts
      state('Starting camera (' + label(a) + ')\u2026');
      return E.create(Object.assign({ prefer: 'auto' }, ENG)).then(function (eng) { engine = eng; return eng.start(); })
        .then(function () {
          state('Round ' + (round + 1) + ': ' + label(a));
          return Calib.run(engine, { method: a.method, lockMethod: true, minAccuracy: 0, goLabel: 'Save this result', allowPassive: false, quick: false });
        });
    }).then(function (r) {
      if (!r) return;
      if (r.action === 'cancel' || !r.score) { state('Round cancelled. Nothing was saved.'); $('hxStudyStart').disabled = false; return; }
      var st = engine.stats ? engine.stats() : {};
      var body = Object.assign(window.HelixStudy.payload(r.score, st), {
        context: 'study', kind: 'calibration', pair_id: pair, calib_points: r.score.calibMode === 'follow' ? 3 : 9,
        arm_method: r.score.calibMode, arm_hires: !!st.hiRes, device: device(), browser: browserTag()
      });
      return fetch(CFG.recordUrl, { method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() }, body: JSON.stringify(body) })
        .then(function (resp) { return resp.json(); }).then(function (j) {
          round++;
          results.push({ arm: arm, score: r.score, hires: !!st.hiRes, res: st.videoW ? st.videoW + 'x' + st.videoH : '', saved: !!j.ok });
          render();
          if (round >= 2) { finish(); return; }
          $('hxStudyStart').textContent = 'Start round 2'; $('hxStudyStart').disabled = false;
          state(j.ok ? 'Round 1 saved' : 'Round 1 not saved (' + esc(j.error) + ')');
        });
    }).catch(function (e) {
      stopEngine(); state('Could not run: ' + (e && e.message || e)); $('hxStudyStart').disabled = false;
    });
  }
  function render() {
    $('hxStudyOut').innerHTML = '<ul class="small mb-0">' + results.map(function (x, i) {
      var s = x.score;
      return '<li>Round ' + (i + 1) + ' (' + esc(label(x.arm)) + (x.arm.hires && !x.hires ? '; the camera did not deliver 1080p' : '') + (x.res ? ', ' + esc(x.res) : '') + '): ' +
        (s.valid ? '~' + s.errorPx + ' px' + (s.errorDeg != null ? ' / ' + s.errorDeg + '\u00b0' : '') : 'no estimates') + (x.saved ? '' : ' (not saved)') + '</li>';
    }).join('') + '</ul>';
  }
  function finish() {
    stopEngine(); ENG.hiRes = false;
    $('hxStudyStart').disabled = true; $('hxStudyStart').textContent = 'Done';
    state('Finished. Thank you.');
    $('hxStudyOut').insertAdjacentHTML('beforeend', '<p class="small mt-2 mb-0">One person\u2019s two rounds say little on their own; the comparison only becomes meaningful across many people and devices. Reload the page to do another pair later.</p>');
  }
  if ($('hxStudyStart')) $('hxStudyStart').addEventListener('click', runRound);
  window.addEventListener('pagehide', stopEngine);
})();
