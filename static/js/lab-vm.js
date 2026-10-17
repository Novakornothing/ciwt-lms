/* Real Linux VM lab: v86 (x86 in WebAssembly) boots Buildroot Linux in the page; serial console terminal.
 * Line mode (default, phone-friendly): a line is sent on Enter; Tab asks the shell to complete; ↑/↓ recall lines.
 * Keys mode (desktop): every key goes straight to the VM (vi, less, Ctrl keys).
 * Grading: "Check my work" drops a probe script into the VM's 9p share, runs it hidden, reads the result back and
 * posts it; the server decides the objectives. Every line sent is posted to the attempt's event log. */
(function () {
  'use strict';
  var cfg = LabKit.config();
  var kit = LabKit.init(cfg);
  var $ = function (id) { return document.getElementById(id); };
  var wrap = $('termWrap'), body = $('termBody'), form = $('termForm'), input = $('termInput'), promptEl = $('termPrompt');
  var status = $('vmStatus'), bar = $('vmBar'), fb = $('vmFeedback'), perf = $('vmPerf');
  var emu = null, booted = false, t0 = 0, raw = false, suppress = null, tabUsed = false;
  var hist = [], hpos = -1, screen = '', cur = null, MAXLINES = 1500;
  var PROMPT_RE = new RegExp(cfg.vm.prompt_re || '[#%$] $');
  var nonce = (cfg.boot && cfg.boot.vm_nonce) || '';
  var DBKEY = cfg.lab_id + ':' + nonce;

  /* ---------------- tiny terminal renderer (serial bytes -> lines) */
  var esc = '', lineCount = 0;
  function newLine() { cur = document.createElement('div'); cur.className = 'ln'; body.appendChild(cur); lineCount++; if (lineCount > MAXLINES) { body.removeChild(body.firstChild); lineCount--; } }
  newLine();
  function put(ch) {
    if (esc) {                                         // swallow ANSI CSI / OSC sequences
      esc += ch;
      if (esc.length === 2 && ch !== '[' && ch !== ']') { esc = ''; }
      else if (esc.length > 2 && /[@-~]/.test(ch) && esc[1] === '[') { if (esc === '\x1b[K' ) {} esc = ''; }
      else if (esc[1] === ']' && (ch === '\x07' || esc.length > 64)) esc = '';
      return;
    }
    if (ch === '\x1b') { esc = ch; return; }
    if (ch === '\r' || ch === '\x07') return;
    if (ch === '\n') { newLine(); screen = ''; return; }
    if (ch === '\b') { var t = cur.textContent; cur.textContent = t.slice(0, -1); screen = screen.slice(0, -1); return; }
    cur.textContent += ch; screen += ch;
  }
  var pending = '', flushT = null;
  function onByte(b) {
    var ch = String.fromCharCode(b);
    if (suppress) { suppress.buf += ch; if (suppress.done && PROMPT_RE.test(suppress.buf.split('\n').pop())) endSuppress(); return; }
    pending += ch;
    if (!flushT) flushT = requestAnimationFrame(flush);
  }
  function flush() {
    flushT = null;
    for (var i = 0; i < pending.length; i++) put(pending[i]);
    pending = '';
    var last = screen;
    var m = last.match(/^(.*?[#%$]) $/);
    if (m) promptEl.textContent = m[1].slice(-24);
    body.scrollTop = body.scrollHeight;
    if (!booted && PROMPT_RE.test(last)) onBooted();
  }
  function idle() { return PROMPT_RE.test(screen); }

  /* ---------------- sending */
  function sendRaw(s) { if (emu) emu.serial0_send(s); }
  var logQ = [], logT = null;
  function logLine(l) { logQ.push(l); if (!logT) logT = setTimeout(postLog, 250); }
  function postLog() {
    logT = null;
    if (!logQ.length) return;
    var lines = logQ.splice(0, 50);
    kit.post(cfg.urls.log, { lines: lines }).then(function (p) { kit.apply(p); }).catch(function () { logQ = lines.concat(logQ); });
  }
  function sendLine(text) {
    var full = text;
    if (tabUsed) { var m = screen.match(/^.*?[#%$] (.*)$/); full = (m ? m[1] : '') + text; tabUsed = false; }
    sendRaw(text + '\n');
    if (full.trim()) { hist.push(full); if (hist.length > 200) hist.shift(); logLine(full); }
    hpos = -1;
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value; input.value = ''; sendLine(v); });
  function tab() { sendRaw(input.value + '\t'); input.value = ''; tabUsed = true; input.focus(); }
  function histMove(d) { if (!hist.length) return; if (hpos === -1) hpos = hist.length; hpos = Math.max(0, Math.min(hist.length, hpos + d)); input.value = hpos === hist.length ? '' : hist[hpos]; }
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Tab') { e.preventDefault(); tab(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); histMove(-1); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); histMove(1); }
    else if (e.ctrlKey && /^[a-z]$/i.test(e.key) && !(e.key.toLowerCase() === 'c' && window.getSelection().toString())) {
      e.preventDefault(); sendRaw(input.value + String.fromCharCode(e.key.toUpperCase().charCodeAt(0) - 64)); input.value = '';
    }
  });
  document.querySelectorAll('[data-key-act]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function (e) {
      e.preventDefault();
      var a = b.getAttribute('data-key-act');
      if (a === 'tab') tab();
      else if (a === 'up') histMove(-1);
      else if (a === 'down') histMove(1);
      else if (a === 'ctrlc') { sendRaw('\x03'); input.value = ''; }
      else if (a === 'ctrld') sendRaw('\x04');
      else if (a === 'esc') sendRaw('\x1b');
      else if (a === 'check') { $('vmCheck').click(); return; }
      else if (a === 'clear') { body.innerHTML = ''; lineCount = 0; newLine(); sendRaw('\x0c'); sendRaw('\n'); }
      if (!raw) input.focus(); else body.focus();
    });
  });
  document.querySelectorAll('[data-chip]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function () { var t = b.getAttribute('data-chip'); input.value = (input.value && !/\s$/.test(input.value) ? input.value + ' ' : input.value) + t; input.focus(); });
  });

  /* keys mode: every key to the VM (desktop keyboards) */
  var KEYS = { Enter: '\r', Backspace: '\x7f', Tab: '\t', Escape: '\x1b', ArrowUp: '\x1b[A', ArrowDown: '\x1b[B', ArrowRight: '\x1b[C', ArrowLeft: '\x1b[D', Home: '\x1b[H', End: '\x1b[F', Delete: '\x1b[3~' };
  var rawLine = '';
  body.addEventListener('keydown', function (e) {
    if (!raw || !emu) return;
    var s = null;
    if (e.ctrlKey && /^[a-z]$/i.test(e.key)) s = String.fromCharCode(e.key.toUpperCase().charCodeAt(0) - 64);
    else if (KEYS[e.key]) s = KEYS[e.key];
    else if (e.key.length === 1 && !e.metaKey) s = e.key;
    if (s === null) return;
    e.preventDefault();
    if (e.key === 'Enter') { var m = screen.match(/^.*?[#%$] (.*)$/); var l = m ? m[1] : rawLine; if (l.trim()) logLine(l); rawLine = ''; }
    else if (e.key.length === 1) rawLine += e.key;
    sendRaw(s);
  });
  body.addEventListener('paste', function (e) { if (!raw) return; e.preventDefault(); sendRaw((e.clipboardData.getData('text') || '').replace(/\n/g, '\r')); });
  $('vmRaw').addEventListener('click', function () {
    raw = !raw;
    this.setAttribute('aria-pressed', raw ? 'true' : 'false');
    this.textContent = raw ? 'Keys: direct' : 'Keys: line';
    form.hidden = raw;
    if (raw) { body.focus(); kit.toast('Direct keys: type in the console. Line mode is easier on phones.', 'ok'); } else input.focus();
  });
  body.addEventListener('click', function () { if (!window.getSelection().toString()) { if (raw) body.focus(); else input.focus(); } });

  /* ---------------- boot */
  function setStatus(t, pct) { status.textContent = t; if (pct !== undefined) { bar.style.width = pct + '%'; bar.parentNode.setAttribute('aria-valuenow', Math.round(pct)); } }
  function loadLib() {
    return new Promise(function (res, rej) {
      if (window.V86) return res();
      var s = document.createElement('script'); s.src = cfg.assets.lib; s.onload = function () { res(); }; s.onerror = function () { rej(new Error('emulator script failed to load')); };
      document.head.appendChild(s);
    });
  }
  function start(initial) {
    $('vmBoot').disabled = true; $('vmResume').disabled = true;
    $('vmProgress').hidden = false;
    setStatus('Loading the emulator…', 3);
    t0 = performance.now();
    loadLib().then(function () {
      var opts = {
        wasm_path: cfg.assets.wasm, memory_size: (cfg.vm.memory_mb || 64) * 1024 * 1024, vga_memory_size: 2 * 1024 * 1024,
        bios: { url: cfg.assets.bios }, vga_bios: { url: cfg.assets.vga_bios },
        cmdline: 'tsc=reliable mitigations=off random.trust_cpu=on',
        filesystem: {}, autostart: true, disable_keyboard: true, disable_mouse: true, disable_speaker: true
      };
      if (initial) opts.initial_state = { buffer: initial }; else opts.bzimage = { url: cfg.assets.bzimage };
      emu = new window.V86(opts);
      window.CIWT_VM = emu;
      emu.add_listener('download-progress', function (e) {
        if (e.lengthComputable && e.total) setStatus('Downloading ' + (e.file_name || '').split('/').pop() + ' — ' + Math.round(e.loaded / 1048576 * 10) / 10 + ' of ' + Math.round(e.total / 1048576 * 10) / 10 + ' MB', 5 + 70 * e.loaded / e.total);
      });
      emu.add_listener('emulator-ready', function () { setStatus('Booting Linux…', 80); });
      emu.add_listener('serial0-output-byte', onByte);
      if (initial) setTimeout(function () { sendRaw('\n'); }, 400);
      $('vmStart').querySelector('.btn') && null;
      wrap.hidden = false;
    }).catch(function (e) { setStatus('Could not start the VM: ' + e.message + '. Try a current Chrome, Edge, Firefox or Safari.', 0); $('vmBoot').disabled = false; });
  }
  function onBooted() {
    booted = true;
    var ms = Math.round(performance.now() - t0);
    setStatus('Ready — booted in ' + (ms / 1000).toFixed(1) + ' s.', 100);
    $('vmTools').hidden = false;
    var mem = (performance.memory && performance.memory.usedJSHeapSize) ? ' · JS heap ' + Math.round(performance.memory.usedJSHeapSize / 1048576) + ' MB' : '';
    perf.textContent = 'This device: boot ' + (ms / 1000).toFixed(1) + ' s' + mem + ' · ' + (navigator.hardwareConcurrency || '?') + ' CPU threads.';
    kit.post(cfg.urls.log, { lines: [], booted: true, boot_ms: ms, ua: navigator.userAgent }).then(function (p) { kit.apply(p); });
    setTimeout(function () { $('vmProgress').hidden = true; }, 1500);
    if (!raw) input.focus({ preventScroll: true });
  }
  $('vmBoot') && $('vmBoot').addEventListener('click', function () { start(null); });

  /* ---------------- grading */
  function endSuppress() {
    var tail = suppress.buf.split('\n').pop();
    var cb = suppress.cb;
    suppress = null;
    if (!(PROMPT_RE.test(screen) && PROMPT_RE.test(tail))) for (var i = 0; i < tail.length; i++) put(tail[i]);
    cb && cb();
  }
  function readResult(tries) {
    return emu.read_file('/.ciwt-result').then(function (u8) {
      var t = new TextDecoder().decode(u8);
      if (!/\nend\s*$/.test(t)) throw new Error('partial');
      return t;
    }).catch(function () {
      if (tries <= 0) throw new Error('The VM did not answer the check (is a program still running? press Ctrl-C).');
      return new Promise(function (r) { setTimeout(r, 150); }).then(function () { return readResult(tries - 1); });
    });
  }
  $('vmCheck').addEventListener('click', function () {
    var btn = this;
    if (!emu || !booted) return;
    if (!idle()) { fb.className = 'lab-feedback bad mt-2'; fb.textContent = 'Finish the current command first (the prompt must be showing), or press Ctrl-C.'; return; }
    btn.disabled = true; fb.className = 'lab-feedback mt-2'; fb.textContent = 'Checking inside the VM…';
    var started = performance.now();
    fetch(cfg.urls.probe, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (j) {
      return emu.create_file('/.ciwt-probe', new TextEncoder().encode(j.script));
    }).then(function () {
      suppress = { buf: '', done: false };
      sendRaw(' sh /mnt/.ciwt-probe; rm -f /mnt/.ciwt-probe\n');
      return readResult(60);
    }).then(function (text) {
      if (suppress) suppress.done = true;
      if (suppress && PROMPT_RE.test(suppress.buf.split('\n').pop())) endSuppress();
      return kit.post(cfg.urls.vmcheck, { probe: text });
    }).then(function (p) {
      kit.apply(p);
      var r = p.result || {};
      var ms = Math.round(performance.now() - started);
      var inFocus = wrap.classList.contains('term-focus');
      if (inFocus) kit.toast(r.error ? r.error : (p.complete ? '✓ All checks passed' : ((r.messages || [])[0] || 'Not yet')), r.error || !p.complete ? 'bad' : 'ok');
      if (r.error) { fb.className = 'lab-feedback bad mt-2'; fb.textContent = r.error; }
      else if (p.complete) { fb.className = 'lab-feedback ok mt-2'; fb.textContent = 'All checks passed (' + ms + ' ms).'; saveVM(true); }
      else {
        fb.className = 'lab-feedback bad mt-2';
        fb.innerHTML = '';
        var ul = document.createElement('ul'); ul.className = 'mb-0';
        (r.messages || []).forEach(function (m) { var li = document.createElement('li'); li.textContent = m; ul.appendChild(li); });
        fb.appendChild(document.createTextNode('Not yet — the VM shows:')); fb.appendChild(ul);
      }
    }).catch(function (e) {
      if (suppress) { suppress.done = true; endSuppress(); }
      fb.className = 'lab-feedback bad mt-2'; fb.textContent = e.message || 'Check failed — try again.';
    }).then(function () { btn.disabled = false; });
  });

  /* ---------------- save / resume on this device (IndexedDB) */
  function idb() {
    return new Promise(function (res, rej) {
      if (!window.indexedDB) return rej(new Error('no IndexedDB'));
      var r = indexedDB.open('ciwt-vm', 1);
      r.onupgradeneeded = function () { r.result.createObjectStore('state'); };
      r.onsuccess = function () { res(r.result); }; r.onerror = function () { rej(r.error); };
    });
  }
  function idbDo(mode, fn) { return idb().then(function (db) { return new Promise(function (res, rej) { var tx = db.transaction('state', mode); var q = fn(tx.objectStore('state')); tx.oncomplete = function () { res(q && q.result); }; tx.onerror = function () { rej(tx.error); }; }); }); }
  function saveVM(quiet) {
    if (!emu) return;
    var t = performance.now();
    emu.save_state().then(function (buf) {
      return idbDo('readwrite', function (s) { s.clear(); return s.put(buf, DBKEY); }).then(function () {
        if (!quiet) kit.toast('VM saved on this device (' + Math.round(buf.byteLength / 1048576) + ' MB, ' + Math.round(performance.now() - t) + ' ms).', 'ok');
      });
    }).catch(function (e) { if (!quiet) kit.toast('Could not save: ' + e.message, 'bad'); });
  }
  $('vmSave').addEventListener('click', function () { saveVM(false); });
  $('vmRestart').addEventListener('click', function () {
    if (!window.confirm('Restart the VM? Unsaved changes inside it are lost (your lab progress is kept).')) return;
    if (emu) { emu.stop(); emu.destroy && emu.destroy(); }
    emu = null; booted = false; body.innerHTML = ''; lineCount = 0; newLine(); screen = ''; start(null);
  });
  idbDo('readonly', function (s) { return s.get(DBKEY); }).then(function (buf) {
    if (buf && $('vmResume')) { $('vmResume').hidden = false; $('vmResume').addEventListener('click', function () { start(buf); }); }
  }).catch(function () {});

  /* ---------------- focus mode (phones), shared look with the simulator terminal */
  var narrow = window.matchMedia('(max-width: 699px)');
  var vv = window.visualViewport;
  function fit() { if (!wrap.classList.contains('term-focus')) return; wrap.style.setProperty('--vvh', (vv ? vv.height : innerHeight) + 'px'); wrap.style.setProperty('--vvtop', (vv ? vv.offsetTop : 0) + 'px'); body.scrollTop = body.scrollHeight; }
  function enterFocus() { wrap.classList.add('term-focus'); document.documentElement.classList.add('term-focus-on'); $('btnFocus').setAttribute('aria-pressed', 'true'); fit(); }
  function exitFocus() { wrap.classList.remove('term-focus'); document.documentElement.classList.remove('term-focus-on'); $('btnFocus').setAttribute('aria-pressed', 'false'); input.blur(); }
  if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
  input.addEventListener('focus', function () { if (narrow.matches) enterFocus(); });
  $('btnFocus').addEventListener('click', function () { if (wrap.classList.contains('term-focus')) exitFocus(); else { enterFocus(); input.focus(); } });
  $('btnFocusExit').addEventListener('click', exitFocus);
  window.addEventListener('beforeunload', function () { if (logQ.length) navigator.sendBeacon && postLog(); });
})();
