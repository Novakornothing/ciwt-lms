/* Exam-Day Readiness Simulator (Option B passes 1 and 4).
   Countdown (server-side pause in practice mode, strict in exam mode), debounced server auto-save of answers, flags and
   the whiteboard, one-question-at-a-time testing-centre view with Previous / Next / Review Screen (scroll view toggle in
   practice mode), skip PBQs and return later, simulation PBQ tabs / read-only terminals / topology nodes, option
   strikethrough (button, Alt+Click or right-click), whiteboard with a CIDR / binary grid helper, review grid.
   The result page only uses the print button at the bottom. */
(function () {
  'use strict';
  var printBtn = document.getElementById('esPrint');
  if (printBtn) printBtn.addEventListener('click', function () { window.print(); });

  var root = document.getElementById('examSim');
  var form = document.getElementById('esForm');
  if (!root || !form) return;
  var strict = root.dataset.strict === '1';
  var left = parseInt(root.dataset.remaining, 10) || 0;
  var clock = document.getElementById('esClock');
  var paused = root.dataset.paused === '1' || root.dataset.pre === '1', submitted = false;
  var pre = root.dataset.pre === '1';
  var qs = Array.prototype.slice.call(document.querySelectorAll('.es-q'));
  var csrf = (form.querySelector('input[name="csrf_token"]') || {}).value || '';
  var saveState = document.getElementById('esSaveState');
  var wbKey = 'esWb:' + root.dataset.attempt;

  function fmt(s) {
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
    return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (x < 10 ? '0' : '') + x;
  }

  // ------------------------------------------------------------ auto-save
  var timer = null;
  function save(now) {
    if (submitted) return;
    clearTimeout(timer);
    timer = setTimeout(function () {
      var fd = new FormData(form);
      fd.append('all', '1');
      saveState.textContent = 'Saving…';
      fetch(root.dataset.autosave, { method: 'POST', body: fd, credentials: 'same-origin',
                                     headers: { 'X-CSRFToken': csrf } })
        .then(function (r) { saveState.textContent = r.ok ? 'All answers saved' : 'Not saved (time expired)'; })
        .catch(function () { saveState.textContent = 'Offline — will retry'; setTimeout(function () { save(true); }, 5000); });
    }, now ? 0 : 800);
  }

  // ------------------------------------------------------------ clock and pause
  function showPaused() {
    var pause = document.getElementById('esPause');
    if (pause) {
      pause.setAttribute('aria-pressed', paused ? 'true' : 'false');
      pause.textContent = paused ? 'Resume timer' : 'Pause timer';
    }
    document.getElementById('esPausedNote').classList.toggle('d-none', !paused || pre);
    document.getElementById('esQuestions').classList.toggle('es-hidden', paused);
  }
  function tick() {
    if (submitted) return;
    if (!paused) left = Math.max(0, left - 1);
    clock.textContent = fmt(left);
    root.classList.toggle('es-low', left <= 300);
    if (left === 0) {
      submitted = true;
      document.getElementById('esTimedOut').value = '1';
      form.submit();
    }
  }
  clock.textContent = fmt(left);
  showPaused();
  setInterval(tick, 1000);
  var pause = document.getElementById('esPause');
  if (pause && !strict) {
    pause.addEventListener('click', function () {
      var fd = new FormData();
      fd.append('csrf_token', csrf);
      fd.append('action', paused ? 'resume' : 'pause');
      fetch(root.dataset.pauseUrl, { method: 'POST', body: fd, credentials: 'same-origin', headers: { 'X-CSRFToken': csrf } })
        .then(function (r) { return r.json(); })
        .then(function (j) { paused = !!j.paused; left = j.remaining; clock.textContent = fmt(left); showPaused(); })
        .catch(function () { paused = !paused; showPaused(); });
    });
  }

  // ------------------------------------------------------------ candidate agreement (clock waits until "I Agree")
  var beginForm = document.getElementById('esBeginForm');
  if (beginForm) {
    beginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      fetch(root.dataset.begin, { method: 'POST', body: new FormData(beginForm), credentials: 'same-origin',
                                  headers: { 'X-CSRFToken': csrf, 'Accept': 'application/json', 'X-Requested-With': 'fetch' } })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          pre = false; paused = false; left = j.remaining; clock.textContent = fmt(left);
          document.getElementById('esAgreement').classList.add('d-none');
          form.classList.remove('es-pre');
          showPaused();
          root.scrollIntoView({ block: 'start' });
        })
        .catch(function () { beginForm.submit(); });
    });
  }

  // ------------------------------------------------------------ one question at a time
  var view = 'single', cur = 0;
  var order = qs.slice();
  var pos = document.getElementById('esPos');
  function show(k) {
    cur = Math.max(0, Math.min(order.length - 1, k));
    order.forEach(function (q, j) { q.classList.toggle('es-off', view === 'single' && j !== cur); });
    form.dataset.view = view;
    pos.textContent = 'Question ' + order[cur].dataset.pos + ' of ' + order.length;
    document.getElementById('esPrev').disabled = cur === 0;
    document.getElementById('esNext').disabled = cur === order.length - 1;
    document.getElementById('esReview').classList.toggle('es-off', view === 'single' && !reviewing);
  }
  var reviewing = false;
  function go(k) { reviewing = false; show(k); save(); if (view === 'single') root.scrollIntoView({ block: 'start' }); }
  document.getElementById('esPrev').addEventListener('click', function () { go(cur - 1); });
  document.getElementById('esNext').addEventListener('click', function () { go(cur + 1); });
  document.getElementById('esReviewBtn').addEventListener('click', function () {
    reviewing = true;
    order.forEach(function (q) { q.classList.toggle('es-off', view === 'single'); });
    document.getElementById('esReview').classList.remove('es-off');
    document.getElementById('esReview').scrollIntoView({ block: 'start' });
    save();
  });
  document.getElementById('esGrid').addEventListener('click', function (e) {
    var a = e.target.closest('.es-cell');
    if (!a || view !== 'single') return;
    e.preventDefault();
    var q = document.getElementById('esq' + a.dataset.n);
    go(order.indexOf(q));
  });
  var vt = document.getElementById('esViewToggle');
  if (vt && !strict) {
    vt.addEventListener('click', function () {
      view = view === 'single' ? 'scroll' : 'single';
      vt.setAttribute('aria-pressed', view === 'scroll' ? 'true' : 'false');
      vt.textContent = view === 'single' ? vt.dataset.scroll : vt.dataset.single;
      document.getElementById('esNav').classList.toggle('es-dim', view === 'scroll');
      show(cur);
    });
  }

  var skip = document.getElementById('esSkipPbq');
  if (skip) {
    skip.addEventListener('click', function () {
      var list = document.getElementById('esQuestions');
      var pbqs = qs.filter(function (q) { return q.classList.contains('es-pbq'); });
      var others = qs.filter(function (q) { return !q.classList.contains('es-pbq'); });
      var skipped = skip.dataset.skipped === '1';
      order = skipped ? pbqs.concat(others) : others.concat(pbqs);
      order.forEach(function (q) { list.appendChild(q); });
      skip.dataset.skipped = skipped ? '0' : '1';
      skip.textContent = skipped ? 'Skip PBQs & return later' : 'Back to PBQs';
      go(0);
    });
  }

  // ------------------------------------------------------------ simulation PBQs
  Array.prototype.forEach.call(document.querySelectorAll('.es-sim'), function (sim) {
    var tabs = sim.querySelectorAll('.es-tab');
    Array.prototype.forEach.call(tabs, function (t) {
      t.addEventListener('click', function () {
        Array.prototype.forEach.call(tabs, function (o) {
          var on = o === t;
          o.classList.toggle('active', on);
          o.setAttribute('aria-selected', on ? 'true' : 'false');
          document.getElementById(o.getAttribute('aria-controls')).classList.toggle('d-none', !on);
        });
      });
    });
    Array.prototype.forEach.call(sim.querySelectorAll('.es-term'), function (term) {
      var out = term.querySelector('.es-out'), inp = term.querySelector('.es-cmd-in');
      function run(cmd) {
        cmd = (cmd || '').trim();
        var tpl = Array.prototype.find.call(term.querySelectorAll('template'), function (t) {
          return t.dataset.cmd.toLowerCase() === cmd.toLowerCase();
        });
        out.textContent = term.dataset.prompt + '> ' + cmd + '\n' +
          (tpl ? tpl.innerHTML.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
               : 'Command not available in this simulation (read-only). Try one of the listed commands.');
      }
      Array.prototype.forEach.call(term.querySelectorAll('.es-cmd'), function (b) {
        b.addEventListener('click', function () { run(b.dataset.cmd); });
      });
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); run(inp.value); inp.value = ''; }
      });
    });
    Array.prototype.forEach.call(sim.querySelectorAll('.es-node'), function (n) {
      n.addEventListener('click', function () {
        Array.prototype.forEach.call(sim.querySelectorAll('.es-node'), function (o) { o.classList.toggle('active', o === n); });
        var d = n.closest('.es-panel').querySelector('.es-node-detail');
        d.textContent = n.textContent + ': ' + n.dataset.detail;
      });
    });
  });

  // ------------------------------------------------------------ option strikethrough (eliminator)
  function strike(opt) {
    var on = opt.classList.toggle('es-struck');
    var b = opt.querySelector('.es-strike');
    if (b) b.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  form.addEventListener('click', function (e) {
    var b = e.target.closest('.es-strike');
    if (b) { e.preventDefault(); strike(b.closest('.es-opt')); return; }
    var opt = e.target.closest('.es-opt');
    if (opt && e.altKey) { e.preventDefault(); strike(opt); }
  });
  form.addEventListener('contextmenu', function (e) {
    var opt = e.target.closest('.es-opt');
    if (opt) { e.preventDefault(); strike(opt); }
  });

  // ------------------------------------------------------------ whiteboard / scratchpad
  var wb = document.getElementById('esWhiteboard'), wbt = document.getElementById('esWbText');
  var wbToggle = document.getElementById('esWbToggle');
  try { if (!wbt.value && sessionStorage.getItem(wbKey)) wbt.value = sessionStorage.getItem(wbKey); } catch (e) { /* private mode */ }
  wbToggle.addEventListener('click', function () {
    var open = wb.classList.toggle('d-none') === false;
    form.classList.toggle('es-wb-open', open);
    wbToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) wbt.focus();
  });
  var GRID = 'Bit value: 128  64  32  16   8   4   2   1\n' +
             'Binary:      _   _   _   _   _   _   _   _\n\n' +
             'CIDR  Mask              Block  Usable hosts\n' +
             '/24   255.255.255.0     256    254\n' +
             '/25   255.255.255.128   128    126\n' +
             '/26   255.255.255.192    64     62\n' +
             '/27   255.255.255.224    32     30\n' +
             '/28   255.255.255.240    16     14\n' +
             '/29   255.255.255.248     8      6\n' +
             '/30   255.255.255.252     4      2\n';
  document.getElementById('esCidr').addEventListener('click', function () {
    wbt.value = (wbt.value ? wbt.value.replace(/\s*$/, '') + '\n\n' : '') + GRID;
    wbt.dispatchEvent(new Event('input', { bubbles: true }));
  });
  document.getElementById('esWbClear').addEventListener('click', function () {
    wbt.value = ''; wbt.dispatchEvent(new Event('input', { bubbles: true }));
  });
  wbt.addEventListener('input', function () {
    try { sessionStorage.setItem(wbKey, wbt.value); } catch (e) { /* private mode */ }
    save();
  });

  // ------------------------------------------------------------ review grid
  function answered(q) {
    return Array.prototype.some.call(q.querySelectorAll('input[name^="q"], select'), function (el) {
      return (el.type === 'radio' || el.type === 'checkbox') ? el.checked : !!el.value;
    });
  }
  function refresh() {
    var a = 0, f = 0;
    qs.forEach(function (q) {
      var n = q.dataset.n, cell = document.querySelector('.es-cell[data-n="' + n + '"]');
      var isA = answered(q), isF = q.querySelector('.es-flag-box').checked;
      a += isA ? 1 : 0; f += isF ? 1 : 0;
      cell.classList.toggle('es-answered', isA);
      cell.classList.toggle('es-unanswered', !isA);
      cell.classList.toggle('es-flagged', isF);
      q.classList.toggle('es-is-flagged', isF);
    });
    document.getElementById('esCounts').textContent =
      'Answered ' + a + ' · Unanswered ' + (qs.length - a) + ' · Flagged ' + f;
  }
  form.addEventListener('change', function (e) {
    refresh();
    if (e.target.id !== 'esWbText') save();
  });
  refresh();
  show(0);

  // ------------------------------------------------------------ testing-centre keyboard shortcuts
  document.addEventListener('keydown', function (e) {
    var t = e.target, tag = (t.tagName || '').toLowerCase();
    if (e.ctrlKey || e.metaKey || e.altKey || pre || paused) return;
    if (tag === 'textarea' || tag === 'select' || (tag === 'input' && !/^(radio|checkbox)$/.test(t.type)) || t.isContentEditable) return;
    var q = order[cur], k = e.key;
    if (k === 'ArrowRight' || k === 'n' || k === 'N') { e.preventDefault(); go(cur + 1); }
    else if (k === 'ArrowLeft' || k === 'p' || k === 'P') { e.preventDefault(); go(cur - 1); }
    else if (k === 'f' || k === 'F') {
      var fb = q.querySelector('.es-flag-box'); fb.checked = !fb.checked;
      fb.dispatchEvent(new Event('change', { bubbles: true }));
    } else if (k === 'w' || k === 'W') { e.preventDefault(); wbToggle.click(); }
    else if (/^[1-6]$/.test(k)) {
      var opt = q.querySelectorAll('.es-opt input')[parseInt(k, 10) - 1];
      if (!opt) return;
      opt.checked = opt.type === 'radio' ? true : !opt.checked;
      opt.dispatchEvent(new Event('change', { bubbles: true }));
      opt.focus();
    }
  });

  form.addEventListener('submit', function (e) {
    if (submitted) return;
    var un = qs.filter(function (q) { return !answered(q); }).length;
    var fl = form.querySelectorAll('.es-flag-box:checked').length;
    if ((un || fl) && !window.confirm('You have ' + un + ' unanswered and ' + fl + ' flagged question(s). Submit anyway?')) {
      e.preventDefault();
      document.getElementById('esReviewBtn').click();
      return;
    }
    submitted = true;
    clearTimeout(timer);
  });
})();
