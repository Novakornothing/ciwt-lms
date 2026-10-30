/* Novak LMS 60-second guided demo. Client-side only; camera preview stays in browser memory. */
(function () {
  'use strict';
  var data = {};
  try { data = JSON.parse(document.getElementById('tourData').textContent || '{}'); } catch (e) { data = {}; }
  var root = document.getElementById('tour');
  var steps = Array.prototype.slice.call(root.querySelectorAll('.step'));
  var bars = Array.prototype.slice.call(root.querySelectorAll('.prog span'));
  var back = document.getElementById('tourBack'), next = document.getElementById('tourNext');
  var stepNo = document.getElementById('stepNo');
  var cur = 0, course = (data.courses && data.courses[0] && data.courses[0].code) || 'ITSUP';
  var stream = null, meterTimer = null;

  function c() { return (data.content && data.content[course]) || {}; }

  function renderWay(i) {
    var ways = c().ways || [];
    root.querySelectorAll('[data-way]').forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-way') === String(i) ? 'true' : 'false'); });
    var body = document.getElementById('wayBody');
    body.innerHTML = ways[i] || '';
    body.querySelectorAll('[data-try]').forEach(function (b) {
      b.addEventListener('click', function () {
        var ok = b.getAttribute('data-try') === 'yes';
        var m = body.querySelector('.msg');
        m.textContent = ok ? (c().tryOk || 'Correct.') : (c().tryMiss || 'Not quite. Try again.');
        m.className = 'msg ' + (ok ? 'ok' : 'miss');
      });
    });
  }

  function renderCourse() {
    root.querySelectorAll('[data-course]').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-course') === course ? 'true' : 'false'); });
    document.getElementById('conceptQ').textContent = c().question || '';
    renderWay(0);
    var lab = c().lab || {};
    document.getElementById('labTask').textContent = lab.task || '';
    document.getElementById('labPrompt').textContent = lab.prompt || '$';
    document.getElementById('labHint').textContent = lab.hint ? 'Hint: ' + lab.hint : '';
    document.getElementById('labOut').textContent = '';
    document.getElementById('labIn').value = '';
  }

  function stopCam() {
    if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
    var box = document.getElementById('camBox'); box.textContent = 'Camera off';
    document.getElementById('camOn').hidden = false; document.getElementById('camOff').hidden = true;
    document.getElementById('eyeStatus').textContent = 'Preview without a camera: sample focus signal.';
  }

  function startMeter() {
    if (meterTimer) return;
    var bar = document.getElementById('meterBar');
    meterTimer = setInterval(function () { bar.style.width = (55 + Math.round(Math.random() * 40)) + '%'; }, 900);
  }
  function stopMeter() { if (meterTimer) { clearInterval(meterTimer); meterTimer = null; } }

  function show(i) {
    cur = Math.max(0, Math.min(steps.length - 1, i));
    steps.forEach(function (s, k) { s.hidden = k !== cur; });
    bars.forEach(function (b, k) { b.className = k <= cur ? 'on' : ''; });
    stepNo.textContent = 'Step ' + (cur + 1) + ' of ' + steps.length;
    back.disabled = cur === 0;
    next.hidden = cur === steps.length - 1;
    if (cur === 2) startMeter(); else { stopMeter(); stopCam(); }
    var h = steps[cur].querySelector('h1'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
    window.scrollTo(0, 0);
    root.setAttribute('data-step-current', String(cur + 1));
  }

  root.querySelectorAll('[data-course]').forEach(function (b) {
    b.addEventListener('click', function () { course = b.getAttribute('data-course'); renderCourse(); });
  });
  root.querySelectorAll('[data-way]').forEach(function (b) {
    b.addEventListener('click', function () { renderWay(parseInt(b.getAttribute('data-way'), 10)); });
  });
  back.addEventListener('click', function () { show(cur - 1); });
  next.addEventListener('click', function () { show(cur + 1); });

  document.getElementById('camOn').addEventListener('click', function () {
    var status = document.getElementById('eyeStatus');
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { status.textContent = 'No camera available. The preview works without one.'; return; }
    navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: false }).then(function (s) {
      stream = s;
      var v = document.createElement('video'); v.autoplay = true; v.muted = true; v.playsInline = true; v.srcObject = s;
      var box = document.getElementById('camBox'); box.textContent = ''; box.appendChild(v);
      document.getElementById('camOn').hidden = true; document.getElementById('camOff').hidden = false;
      status.textContent = 'Camera on. The picture never leaves this page.';
    }).catch(function () { status.textContent = 'Camera not allowed. That is fine: the preview works without it.'; });
  });
  document.getElementById('camOff').addEventListener('click', stopCam);

  document.getElementById('labForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var lab = c().lab || {}, v = (document.getElementById('labIn').value || '').trim().replace(/\s+/g, ' ').toLowerCase();
    var out = document.getElementById('labOut');
    var ok = (lab.accept || []).some(function (a) { return v === a; });
    out.textContent = ok ? (lab.output || '') + '\n\u2713 ' + (lab.ok || 'Correct.') : (v ? '\u2717 ' + (lab.miss || 'Not quite. Check the hint and try again.') : 'Type a command first.');
    out.style.color = ok ? '#b9f3cf' : '#ffc9bd';
    root.setAttribute('data-lab-ok', ok ? '1' : '0');
  });

  document.querySelectorAll('[data-view]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-view');
      document.querySelectorAll('[data-view]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('[data-viewpane]').forEach(function (p) { p.hidden = p.getAttribute('data-viewpane') !== v; });
    });
  });

  window.addEventListener('pagehide', stopCam);
  renderCourse();
  show(0);
})();
