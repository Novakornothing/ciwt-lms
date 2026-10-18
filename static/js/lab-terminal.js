/* CIWT live labs — terminal client (Windows cmd/PowerShell, IOS switch/router, Linux bash, ticket desk).
 * Server-side state: every command is POSTed and the transcript is stored, so a reload resumes exactly.
 * Mobile: keys bar (Tab ↑ ↓ Ctrl-C Clear ?), command chips that insert text, a focus mode sized to the
 * visual viewport so the on-screen keyboard never covers the prompt, 16px input (no iOS zoom). */
(function () {
  'use strict';
  var cfg = LabKit.config();
  if (!cfg) return;
  var kit = LabKit.init(cfg);
  var wrap = document.getElementById('termWrap');
  var body = document.getElementById('termBody');
  var input = document.getElementById('termInput');
  var promptEl = document.getElementById('termPrompt');
  var form = document.getElementById('termForm');
  var hist = [], hpos = -1, busy = false, queue = [];
  var narrow = window.matchMedia('(max-width: 699.98px)');

  function line(text, cls) {
    var d = document.createElement('div');
    d.className = 'term-line' + (cls ? ' ' + cls : '');
    d.textContent = text;
    body.appendChild(d);
    return d;
  }
  function scroll() { body.scrollTop = body.scrollHeight; }
  function setPrompt(p) { if (p !== undefined && p !== null) promptEl.textContent = p; }

  // resume: transcript from the server
  (cfg.boot.transcript || []).forEach(function (t) {
    line(t.t, t.c === 'cmd' ? 'cmd' : (t.c === 'sys' ? 'sys' : ''));
    if (t.c === 'cmd') {
      var c = t.t.replace(/^.*?[>#$]\s?/, '');
      if (c) hist.push(c);
    }
  });
  if (!(cfg.boot.transcript || []).length) {
    line(cfg.welcome || 'Type help (or ?) for commands. Tab completes.', 'sys');
  } else {
    line('— resumed: your earlier work is above —', 'sys');
  }
  setPrompt(cfg.boot.prompt);
  scroll();

  function send(cmd) {
    if (busy) { queue.push(cmd); return; }
    busy = true;
    var shown = promptEl.textContent + ' ' + cmd;
    var echo = line(shown, 'cmd');
    if (cmd.trim()) { hist.push(cmd); if (hist.length > 100) hist.shift(); }
    hpos = -1;
    scroll();
    kit.post(cfg.urls.cmd, { command: cmd }).then(function (p) {
      if (p.clear) { body.innerHTML = ''; }
      (p.lines || []).forEach(function (t) { line(t, /^(% |'|.*not recognized|.*command not found|.*Invalid)/.test(t) ? 'err' : ''); });
      setPrompt(p.prompt);
      kit.apply(p);
      scroll();
      checkpointDue(p);
    }).catch(function () {
      echo.classList.add('failed');
      var r = line('(not sent — connection problem) ', 'err');
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'btn btn-sm btn-outline-light term-retry'; b.textContent = 'Retry';
      b.addEventListener('click', function () { r.remove(); echo.remove(); send(cmd); });
      r.appendChild(b);
      scroll();
    }).then(function () {
      busy = false;
      if (queue.length) send(queue.shift());
    });
  }

  // when every command objective is met but a checkpoint question remains, leave focus mode and show it
  var cpShown = false;
  function checkpointDue(p) {
    if (cpShown || !p.steps || !p.steps.length) return;
    var done = p.done || [];
    var stepObj = p.steps.map(function (s) { return s.objective; });
    var cmdLeft = (p.objectives || []).some(function (o) { return stepObj.indexOf(o.id) < 0 && done.indexOf(o.id) < 0; });
    var open = p.steps.filter(function (s) { return done.indexOf(s.objective) < 0; })[0];
    if (cmdLeft || !open) return;
    cpShown = true;
    if (wrap.classList.contains('term-focus')) exitFocus();
    kit.toast('Commands done — answer the checkpoint below.', 'ok');
    var card = document.querySelector('[data-step="' + open.id + '"]');
    if (card) setTimeout(function () { card.scrollIntoView({ block: 'start', behavior: 'smooth' }); var h = card.querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } }, 150);
  }

  function tab() {
    var partial = input.value;
    kit.post(cfg.urls.complete, { partial: partial }).then(function (r) {
      if (r.text !== undefined && r.text !== null) input.value = r.text;
      if (r.options && r.options.length > 1) { line(r.options.join('   '), 'sys'); scroll(); }
      else if (r.beep && !(r.options || []).length) { wrap.classList.add('beep'); setTimeout(function () { wrap.classList.remove('beep'); }, 160); }
      input.focus();
      var n = input.value.length; try { input.setSelectionRange(n, n); } catch (e) { /* noop */ }
    });
  }
  function histMove(dir) {
    if (!hist.length) return;
    if (hpos === -1) hpos = hist.length;
    hpos = Math.max(0, Math.min(hist.length, hpos + dir));
    input.value = hpos === hist.length ? '' : hist[hpos];
    var n = input.value.length; try { input.setSelectionRange(n, n); } catch (e) { /* noop */ }
  }
  function ctrlC() { line(promptEl.textContent + ' ' + input.value + '^C', 'cmd'); input.value = ''; hpos = -1; scroll(); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var c = input.value;
    input.value = '';
    send(c);
    if (wrap.classList.contains('term-focus') && document.activeElement !== input) input.focus({ preventScroll: true });
  });
  // r5: tapping ↵ must not take focus from the input (that closed the phone keyboard after every command)
  var sendBtn = form.querySelector('.term-send');
  if (sendBtn) sendBtn.addEventListener('pointerdown', function (e) { e.preventDefault(); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Tab') { e.preventDefault(); tab(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); histMove(-1); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); histMove(1); }
    else if (e.ctrlKey && (e.key === 'c' || e.key === 'C') && !window.getSelection().toString()) { e.preventDefault(); ctrlC(); }
    else if (e.ctrlKey && (e.key === 'l' || e.key === 'L')) { e.preventDefault(); send('clear'); }
    else if (e.key === 'Escape' && wrap.classList.contains('term-focus')) { exitFocus(); }
  });
  body.addEventListener('click', function () { if (!window.getSelection().toString()) input.focus(); });

  // keys bar: pointerdown + preventDefault keeps the on-screen keyboard open
  document.querySelectorAll('[data-key-act]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function (e) {
      e.preventDefault();
      var a = b.getAttribute('data-key-act');
      if (a === 'tab') tab();
      else if (a === 'up') histMove(-1);
      else if (a === 'down') histMove(1);
      else if (a === 'ctrlc') ctrlC();
      else if (a === 'clear') send('clear');
      else if (a === 'help') send(cfg.kind === 'switch' || cfg.kind === 'router' ? '?' : 'help');
      else if (a === 'hint') kit.hint();
      input.focus();
    });
  });
  // command chips insert text (they never run it)
  document.querySelectorAll('[data-chip]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function (e) {
      e.preventDefault();
      var t = b.getAttribute('data-chip');
      var v = input.value;
      input.value = (v && !/\s$/.test(v) && !/^\s/.test(t) && v.length ? v + ' ' : v) + t;
      input.focus();
      var n = input.value.length; try { input.setSelectionRange(n, n); } catch (er) { /* noop */ }
    });
  });

  // undo: reload the transcript from the server to show the reverted state
  kit.onUndo = function (p) { if (p.undone) { line('(last change undone)', 'sys'); setPrompt(p.prompt); scroll(); } };

  // ---- phone focus mode: fixed overlay sized to the visual viewport (survives the keyboard)
  var vv = window.visualViewport;
  function fit() {
    if (!wrap.classList.contains('term-focus')) return;
    var h = vv ? vv.height : window.innerHeight;
    var top = vv ? vv.offsetTop : 0;
    wrap.style.setProperty('--vvh', h + 'px');
    wrap.style.setProperty('--vvtop', top + 'px');
    wrap.classList.toggle('term-short', h < 560);   // r5: keyboard open — drop the chips row, keep prompt + keys
    scroll();
  }
  function enterFocus() {
    if (wrap.classList.contains('term-focus')) return;
    wrap.classList.add('term-focus');
    document.documentElement.classList.add('term-focus-on');
    document.getElementById('btnFocus').setAttribute('aria-pressed', 'true');
    fit();
  }
  function exitFocus() {
    wrap.classList.remove('term-focus', 'term-short');
    document.documentElement.classList.remove('term-focus-on');
    var tn = document.getElementById('termNote'); if (tn) tn.hidden = true;
    document.getElementById('btnFocus').setAttribute('aria-pressed', 'false');
    wrap.style.removeProperty('--vvh');
    input.blur();
  }
  if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
  window.addEventListener('orientationchange', function () { setTimeout(fit, 250); });
  input.addEventListener('focus', function () { if (narrow.matches && cfg.autoFocusMode !== false) enterFocus(); setTimeout(scroll, 300); });
  var fb = document.getElementById('btnFocus');
  if (fb) fb.addEventListener('click', function () { if (wrap.classList.contains('term-focus')) exitFocus(); else { enterFocus(); input.focus(); } });
  var xb = document.getElementById('btnFocusExit');
  if (xb) xb.addEventListener('click', exitFocus);
  window.CIWT_TERM = { send: send, el: input };
})();
