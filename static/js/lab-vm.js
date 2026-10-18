/* Real Linux VM labs: v86 (x86 in WebAssembly) boots Buildroot Linux in the page — one or more machines, each with
 * its own serial console, optionally cabled to a virtual network (lab-vmnet.js: isolating switch + DHCP/DNS host).
 *  - Line mode (default, phone-friendly): a line is sent on Enter; Tab asks the shell to complete; ↑/↓ recall lines.
 *  - Keys mode (desktop): every key goes straight to the VM (vi, less, top, Ctrl keys).
 *  - Setup: after the first boot the lab's scenario script is dropped into each VM's 9p share and sourced (hidden).
 *    A clean snapshot is then kept in memory so "Reset VM" is instant.
 *  - Grading: "Check my work" runs the server's probe in each VM (hidden), reads the results back and posts them with
 *    the virtual network's evidence; the server decides the objectives. Every line sent is logged to the attempt.
 *  - Save: the whole machine state (all VMs + DHCP leases) goes to IndexedDB on this device; Resume restores it. */
(function () {
  'use strict';
  var cfg = LabKit.config();
  var kit = LabKit.init(cfg);
  var $ = function (id) { return document.getElementById(id); };
  var VMC = cfg.vm || {};
  var SPECS = VMC.machines && VMC.machines.length ? VMC.machines : [{ name: 'vm', label: 'VM', memory_mb: 64 }];
  var MULTI = SPECS.length > 1;
  var PROMPT_RE = new RegExp(VMC.prompt_re || '[#%$] $');
  var LINE_PROMPT = /^(.*?[#%$]) $/;
  var wrap = $('termWrap'), form = $('termForm'), input = $('termInput'), promptEl = $('termPrompt');
  var status = $('vmStatus'), bar = $('vmBar'), fb = $('vmFeedback'), perf = $('vmPerf'), titleEl = $('vmTitle');
  var nonce = (cfg.boot && cfg.boot.vm_nonce) || '';
  var DBKEY = cfg.lab_id + ':' + nonce;
  var raw = false, t0 = 0, started = false, allReady = false, cleanSnap = null;
  var fabric = null, services = null, MAXLINES = 1500;

  /* ---------------------------------------------------------------- machines + their consoles */
  function Machine(spec) {
    this.spec = spec; this.name = spec.name; this.label = spec.label || spec.name;
    this.screenEl = document.querySelector('.vm-screen[data-m="' + spec.name + '"]');
    this.cur = null; this.scr = ''; this.esc = ''; this.lines = 0; this.pending = ''; this.flushT = null;
    this.suppress = null; this.booted = false; this.ready = false; this.hist = []; this.hpos = -1; this.tabUsed = false;
    this.emu = null; this.rawLine = ''; this.disk = null;
    this.dec = window.TextDecoder ? new TextDecoder('utf-8') : null; this.pb = [];   // console bytes are UTF-8 (lsblk trees, quotes)
    this.newLine();
  }
  Machine.prototype.newLine = function () {
    this.cur = document.createElement('div'); this.cur.className = 'ln'; this.screenEl.appendChild(this.cur); this.lines++;
    if (this.lines > MAXLINES) { this.screenEl.removeChild(this.screenEl.firstChild); this.lines--; }
  };
  Machine.prototype.clearScreen = function () { this.screenEl.innerHTML = ''; this.lines = 0; this.newLine(); this.scr = ''; };
  Machine.prototype.put = function (ch) {
    if (this.esc) {                                      // swallow ANSI CSI / OSC sequences
      this.esc += ch;
      if (this.esc.length === 2 && ch !== '[' && ch !== ']') this.esc = '';
      else if (this.esc.length > 2 && this.esc[1] === '[' && /[@-~]/.test(ch)) this.esc = '';
      else if (this.esc[1] === ']' && (ch === '\x07' || this.esc.length > 64)) this.esc = '';
      return;
    }
    if (ch === '\x1b') { this.esc = ch; return; }
    if (ch === '\r' || ch === '\x07') return;
    if (ch === '\n') { this.newLine(); this.scr = ''; return; }
    if (ch === '\b') { this.cur.textContent = this.cur.textContent.slice(0, -1); this.scr = this.scr.slice(0, -1); return; }
    this.cur.textContent += ch; this.scr += ch;
  };
  Machine.prototype.onByte = function (b) {
    var ch = String.fromCharCode(b), self = this;
    if (this.suppress) {
      this.suppress.buf += ch;
      if (this.suppress.done && PROMPT_RE.test(this.suppress.buf.split('\n').pop())) this.endSuppress();
      return;
    }
    this.pb.push(b);
    if (!this.flushT) this.flushT = requestAnimationFrame(function () { self.flush(); });
  };
  Machine.prototype.flush = function () {
    this.flushT = null;
    var txt = this.dec ? this.dec.decode(new Uint8Array(this.pb), { stream: true }) : String.fromCharCode.apply(null, this.pb);
    this.pb = [];
    for (var i = 0; i < txt.length; i++) this.put(txt[i]);
    if (this === active) syncPrompt();
    this.screenEl.scrollTop = this.screenEl.scrollHeight;
    if (!this.booted && PROMPT_RE.test(this.scr)) this.onBooted();
  };
  Machine.prototype.idle = function () { return PROMPT_RE.test(this.scr); };
  Machine.prototype.send = function (s) { if (this.emu) this.emu.serial0_send(s); };
  /* run a script hidden: drop it into the 9p share, source or sh it, swallow the output until the prompt returns */
  Machine.prototype.hidden = function (path, text, how) {
    var self = this;
    return this.emu.create_file('/' + path, new TextEncoder().encode(text)).then(function () {
      return new Promise(function (res) {
        self.suppress = { buf: '', done: false, cb: res };
        self.send(' ' + how + ' /mnt/' + path + '; rm -f /mnt/' + path + '\n');
        setTimeout(function () { if (self.suppress) self.suppress.done = true; if (self.suppress && PROMPT_RE.test(self.suppress.buf.split('\n').pop())) self.endSuppress(); }, 50);
      });
    });
  };
  Machine.prototype.endSuppress = function () {
    var s = this.suppress; this.suppress = null;
    var tail = s.buf.split('\n').pop();
    if (!(PROMPT_RE.test(this.scr) && PROMPT_RE.test(tail))) {
      // the prompt may have changed (setup sets PS1): replace the current line with the new prompt
      this.cur.textContent = ''; this.scr = '';
      for (var i = 0; i < tail.length; i++) this.put(tail[i]);
    }
    if (this === active) syncPrompt();
    s.cb && s.cb(s.buf);
  };
  Machine.prototype.onBooted = function () {
    var self = this;
    this.booted = true;
    if (this.resumed || !(VMC.setup && VMC.setup[this.name])) { this.ready = true; return checkAllReady(); }
    setStatus('Preparing the scenario on ' + this.label + '…', 92);
    this.hidden('.ciwt-setup', VMC.setup[this.name], '.').then(function () { self.ready = true; checkAllReady(); });
  };

  var machines = SPECS.map(function (s) { return new Machine(s); });
  var byName = {}; machines.forEach(function (m) { byName[m.name] = m; });
  var active = machines[0];

  var PW_RE = /(pass(word|phrase)[^\n]*|PIN):\s*$/i;
  function syncPrompt() {
    var m = active.scr.match(LINE_PROMPT), pw = !raw && PW_RE.test(active.scr);
    promptEl.textContent = raw ? 'keys' : (pw ? 'password' : (m ? m[1].slice(-26) : (active.ready ? '$' : '…')));
    var t = pw ? 'password' : 'text';
    if (input.type !== t) { input.type = t; input.setAttribute('autocomplete', pw ? 'off' : 'off'); }
  }

  /* ---------------------------------------------------------------- tabs (machines + Packets) */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-vm-tab]'));
  var packetsEl = $('vmPackets');
  function showTab(name) {
    tabs.forEach(function (t) { var on = t.getAttribute('data-vm-tab') === name; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
    machines.forEach(function (m) { m.screenEl.hidden = m.name !== name; });
    if (packetsEl) packetsEl.hidden = name !== '_packets';
    form.hidden = name === '_packets';
    if (byName[name]) {
      active = byName[name];
      if (titleEl) titleEl.textContent = 'root@' + (active.spec.hostname || active.label) + ' — real Linux (BusyBox sh)';
      syncPrompt();
      active.screenEl.scrollTop = active.screenEl.scrollHeight;
      if (started) input.focus({ preventScroll: true });
    } else if (packetsEl) { packetsEl.scrollTop = packetsEl.scrollHeight; }
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { showTab(t.getAttribute('data-vm-tab')); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : (e.key === 'ArrowLeft' ? -1 : 0);
      if (d) { e.preventDefault(); var n = tabs[(i + d + tabs.length) % tabs.length]; n.focus(); n.click(); }
    });
  });

  /* ---------------------------------------------------------------- sending + logging */
  var logQ = [], logT = null;
  function logLine(m, l) { logQ.push(MULTI ? '[' + m.name + '] ' + l : l); if (!logT) logT = setTimeout(postLog, 250); }
  function postLog() {
    logT = null;
    if (!logQ.length) return Promise.resolve();
    var lines = logQ.splice(0, 50);
    return kit.post(cfg.urls.log, { lines: lines }).then(function (p) { kit.apply(p); if (logQ.length) return postLog(); })
      .catch(function () { logQ = lines.concat(logQ); });
  }
  function sendLine(text) {
    var m = active, full = text;
    if (!m.emu || !m.ready) { kit.toast(m.booted ? 'Preparing the scenario — one moment.' : 'Start the VM first.', 'bad'); return; }
    if (PW_RE.test(m.scr)) { m.send(text + '\n'); logLine(m, '(password typed — not logged)'); m.hpos = -1; return; }
    if (m.tabUsed) { var mm = m.scr.match(/^.*?[#%$] (.*)$/); full = (mm ? mm[1] : '') + text; m.tabUsed = false; }
    m.send(text + '\n');
    if (full.trim()) { m.hist.push(full); if (m.hist.length > 200) m.hist.shift(); logLine(m, full); }
    m.hpos = -1;
  }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (raw) { rawFlushInput(); rawEnter(active); active.send('\r'); }
    else { var v = input.value; input.value = ''; sendLine(v); }
    if (wrap.classList.contains('term-focus') && document.activeElement !== input) input.focus({ preventScroll: true });
  });
  // r5: tapping ↵ must not take focus from the input (that closed the phone keyboard after every line)
  var sendBtn = form.querySelector('.term-send');
  if (sendBtn) sendBtn.addEventListener('pointerdown', function (e) { e.preventDefault(); });
  function tab() { active.send(input.value + '\t'); input.value = ''; active.tabUsed = true; input.focus(); }
  function histMove(d) {
    var m = active; if (!m.hist.length) return;
    if (m.hpos === -1) m.hpos = m.hist.length;
    m.hpos = Math.max(0, Math.min(m.hist.length, m.hpos + d));
    input.value = m.hpos === m.hist.length ? '' : m.hist[m.hpos];
  }
  input.addEventListener('keydown', function (e) {
    if (raw) {   // direct keys through the input: special keys here, printable text via input/composition events below
      var s = null;
      if (e.ctrlKey && /^[a-z]$/i.test(e.key)) s = String.fromCharCode(e.key.toUpperCase().charCodeAt(0) - 64);
      else if (KEYS[e.key] && !(e.key === 'Backspace' && input.value)) s = KEYS[e.key];
      if (s === null || !active.emu) return;
      e.preventDefault(); rawFlushInput();
      if (e.key === 'Enter') rawEnter(active);
      else if (e.key === 'Backspace') active.rawLine = active.rawLine.slice(0, -1);
      else if (e.key === 'Escape' || (e.ctrlKey && /^[cu]$/i.test(e.key))) active.rawLine = '';
      active.send(s);
      return;
    }
    if (e.key === 'Tab') { e.preventDefault(); tab(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); histMove(-1); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); histMove(1); }
    else if (e.ctrlKey && /^[a-z]$/i.test(e.key) && !(e.key.toLowerCase() === 'c' && window.getSelection().toString())) {
      e.preventDefault(); active.send(input.value + String.fromCharCode(e.key.toUpperCase().charCodeAt(0) - 64)); input.value = '';
    }
  });
  document.querySelectorAll('[data-key-act]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function (e) {
      e.preventDefault();
      var a = b.getAttribute('data-key-act');
      if (raw && (a === 'tab' || a === 'up' || a === 'down' || a === 'clear')) { rawFlushInput(); active.send({ tab: '\t', up: '\x1b[A', down: '\x1b[B', clear: '\x0c' }[a]); }
      else if (a === 'tab') tab();
      else if (a === 'up') histMove(-1);
      else if (a === 'down') histMove(1);
      else if (a === 'ctrlc') { active.send('\x03'); input.value = ''; active.rawLine = ''; }
      else if (a === 'ctrld') active.send('\x04');
      else if (a === 'esc') { if (raw) rawFlushInput(); active.rawLine = ''; active.send('\x1b'); }
      else if (a === 'check') { $('vmCheck').click(); return; }
      else if (a === 'hint') kit.hint();
      else if (a === 'clear') { active.clearScreen(); active.send('\n'); }
      input.focus();
    });
  });
  document.querySelectorAll('[data-chip]').forEach(function (b) {
    b.addEventListener('pointerdown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function () { var t = b.getAttribute('data-chip'); input.value = (input.value && !/\s$/.test(input.value) ? input.value + ' ' : input.value) + t; input.focus(); });
  });

  /* keys mode: every key to the VM (desktop keyboards) */
  var KEYS = { Enter: '\r', Backspace: '\x7f', Tab: '\t', Escape: '\x1b', ArrowUp: '\x1b[A', ArrowDown: '\x1b[B', ArrowRight: '\x1b[C', ArrowLeft: '\x1b[D', Home: '\x1b[H', End: '\x1b[F', Delete: '\x1b[3~' };
  machines.forEach(function (m) {
    m.screenEl.addEventListener('keydown', function (e) {
      if (!raw || !m.emu) return;
      var s = null;
      if (e.ctrlKey && /^[a-z]$/i.test(e.key)) s = String.fromCharCode(e.key.toUpperCase().charCodeAt(0) - 64);
      else if (KEYS[e.key]) s = KEYS[e.key];
      else if (e.key.length === 1 && !e.metaKey) s = e.key;
      if (s === null) return;
      e.preventDefault();
      if (e.key === 'Enter') rawEnter(m);
      else if (e.key === 'Escape' || (e.ctrlKey && /^[cu]$/i.test(e.key))) m.rawLine = '';
      else if (e.key === 'Backspace') m.rawLine = m.rawLine.slice(0, -1);
      else if (e.key.length === 1 && !e.ctrlKey) m.rawLine += e.key;
      m.send(s);
    });
    m.screenEl.addEventListener('paste', function (e) { if (!raw) return; e.preventDefault(); m.send((e.clipboardData.getData('text') || '').replace(/\n/g, '\r')); });
    m.screenEl.addEventListener('click', function () { if (!window.getSelection().toString()) input.focus(); });
  });
  $('vmRaw').addEventListener('click', function () {
    raw = !raw;
    this.setAttribute('aria-pressed', raw ? 'true' : 'false');
    this.textContent = raw ? 'Keys: direct' : 'Keys: line';
    input.value = ''; input.type = 'text';
    input.setAttribute('aria-label', raw ? 'Direct keys: every key goes to the VM' : '');
    if (!raw) input.removeAttribute('aria-label');
    syncPrompt();
    input.focus();
    if (raw) kit.toast('Direct keys: every key goes straight to the VM (vi, Ctrl keys). Full-screen programs draw roughly in this console, so prefer sed, cat or top -b -n 1. Esc, Ctrl-C and the arrows are on the keys bar.', 'ok');
  });

  /* r5: direct keys work through the input as well, so phones can use them: a focused <div> opens no on-screen
   * keyboard. Printable text comes from input/composition events (Android keyboards send keyCode 229, not keys). */
  var composing = false;
  // what was typed (the screen echo can lag behind fast typing on a slow phone, so it is only the fallback)
  function rawEnter(m) { var mm = m.scr.match(/^.*?[#%$] (.*)$/); var l = m.rawLine.trim() ? m.rawLine : (mm ? mm[1] : ''); if (l.trim()) logLine(m, l); m.rawLine = ''; }
  function rawFlushInput() { var v = input.value; if (!v || !active.emu) return; input.value = ''; active.rawLine += v; active.send(v.replace(/\n/g, '\r')); }
  input.addEventListener('compositionstart', function () { composing = true; });
  input.addEventListener('compositionend', function () { composing = false; if (raw) rawFlushInput(); });
  input.addEventListener('input', function (e) { if (raw && !composing && !e.isComposing) rawFlushInput(); });
  input.addEventListener('beforeinput', function (e) {
    if (!raw || !active.emu) return;
    if (e.inputType === 'deleteContentBackward' && !input.value) { e.preventDefault(); active.rawLine = active.rawLine.slice(0, -1); active.send('\x7f'); }
    else if (e.inputType === 'insertLineBreak' || e.inputType === 'insertParagraph') { e.preventDefault(); rawFlushInput(); rawEnter(active); active.send('\r'); }
  });

  /* ---------------------------------------------------------------- network */
  function buildNet(snapshot) {
    if (!VMC.net || !window.VMNet) return;
    fabric = new window.VMNet.Fabric({ max_log: 400 });
    if (packetsEl) {
      packetsEl.innerHTML = '';
      fabric.onframe = function (r) {
        var d = document.createElement('div'); d.className = 'ln pk';
        d.textContent = '#' + r.n + '  ' + r.from + '  ' + r.s;
        packetsEl.appendChild(d);
        if (packetsEl.childNodes.length > 300) packetsEl.removeChild(packetsEl.firstChild);
        if (!packetsEl.hidden) packetsEl.scrollTop = packetsEl.scrollHeight;
      };
    }
    machines.forEach(function (m) {
      var port = fabric.attach(m.label, m.spec.segs || [], function (frame) { if (m.emu) m.emu.bus.send('net0-receive', frame); });
      m.port = port;
    });
    if (VMC.net.services) {
      var sc = JSON.parse(JSON.stringify(VMC.net.services)); sc.state = snapshot || null;
      services = new window.VMNet.Services(fabric, sc);
    }
  }

  /* ---------------------------------------------------------------- boot */
  function setStatus(t, pct) { status.textContent = t; if (pct !== undefined) { bar.style.width = pct + '%'; bar.parentNode.setAttribute('aria-valuenow', Math.round(pct)); } }
  function loadScript(src, test) {
    return new Promise(function (res, rej) {
      if (test()) return res();
      var s = document.createElement('script'); s.src = src; s.onload = function () { res(); }; s.onerror = function () { rej(new Error('emulator script failed to load')); };
      document.head.appendChild(s);
    });
  }
  var slowTimer = null;
  function start(saved) {
    started = true; allReady = false;
    $('vmBoot').disabled = true; if ($('vmResume')) $('vmResume').disabled = true;
    $('vmProgress').hidden = false;
    setStatus('Loading the emulator…', 3);
    t0 = performance.now();
    clearTimeout(slowTimer);
    slowTimer = setTimeout(function () { if (!allReady) showWeak('This device is taking a while to boot the VM.'); }, 60000);
    var libs = loadScript(cfg.assets.lib, function () { return !!window.V86; });
    if (VMC.net) libs = libs.then(function () { return loadScript(cfg.assets.net, function () { return !!window.VMNet; }); });
    libs.then(function () {
      buildNet(saved && saved.net);
      var loaded = {};
      machines.forEach(function (m) {
        var opts = {
          wasm_path: cfg.assets.wasm, memory_size: (m.spec.memory_mb || 64) * 1024 * 1024, vga_memory_size: 2 * 1024 * 1024,
          bios: { url: cfg.assets.bios }, vga_bios: { url: cfg.assets.vga_bios },
          cmdline: 'tsc=reliable mitigations=off random.trust_cpu=on',
          filesystem: {}, autostart: true, disable_keyboard: true, disable_mouse: true, disable_speaker: true
        };
        if (VMC.net) opts.net_device = { type: 'ne2k' };
        var st = saved && saved.machines && saved.machines[m.name];
        m.resumed = !!st;
        if (m.spec.disk_mb) {
          m.disk = (st && saved.disks && saved.disks[m.name]) || new ArrayBuffer(m.spec.disk_mb * 1024 * 1024);
          opts.hda = { buffer: m.disk };
        }
        if (st) opts.initial_state = { buffer: st }; else opts.bzimage = { url: cfg.assets.bzimage };
        m.emu = new window.V86(opts);
        m.emu.add_listener('download-progress', function (e) {
          if (e.lengthComputable && e.total) { loaded[e.file_name] = [e.loaded, e.total]; var a = 0, b = 0; Object.keys(loaded).forEach(function (k) { a += loaded[k][0]; b += loaded[k][1]; });
            setStatus('Downloading the VM — ' + Math.round(a / 1048576 * 10) / 10 + ' of ' + Math.round(b / 1048576 * 10) / 10 + ' MB', 5 + 70 * a / b); }
        });
        m.emu.add_listener('emulator-ready', function () { setStatus('Booting Linux' + (MULTI ? ' on ' + machines.length + ' machines' : '') + '…', 80); });
        m.emu.add_listener('serial0-output-byte', function (b) { m.onByte(b); });
        if (m.port) m.emu.add_listener('net0-send', function (d) { m.port.send(new Uint8Array(d)); });
        if (st) setTimeout(function () { m.send('\n'); }, 500);
      });
      window.CIWT_VM = machines[0].emu;
      window.CIWT_VMS = byName;
      window.CIWT_NET = { fabric: fabric, services: services };
      wrap.hidden = false;
      showTab(active.name);
    }).catch(function (e) { setStatus('Could not start the VM: ' + e.message + '. Try a current Chrome, Edge, Firefox or Safari.', 0); $('vmBoot').disabled = false; showWeak('The VM could not start here.'); });
  }
  function checkAllReady() {
    if (allReady || !machines.every(function (m) { return m.ready; })) return;
    allReady = true;
    clearTimeout(slowTimer);
    var ms = Math.round(performance.now() - t0);
    setStatus('Ready — ' + (MULTI ? machines.length + ' machines ' : '') + 'booted in ' + (ms / 1000).toFixed(1) + ' s.', 100);
    $('vmTools').hidden = false;
    var mem = (performance.memory && performance.memory.usedJSHeapSize) ? ' · JS heap ' + Math.round(performance.memory.usedJSHeapSize / 1048576) + ' MB' : '';
    perf.textContent = 'This device: boot ' + (ms / 1000).toFixed(1) + ' s' + mem + ' · ' + (navigator.hardwareConcurrency || '?') + ' CPU threads.';
    kit.post(cfg.urls.log, { lines: [], booted: true, boot_ms: ms, ua: navigator.userAgent }).then(function (p) { kit.apply(p); });
    setTimeout(function () { $('vmProgress').hidden = true; }, 1500);
    machines.forEach(function (m) { if (m.resumed) m.send('\n'); });
    snapshotClean();
    input.focus({ preventScroll: true });
    if (ms > 45000) showWeak('Booting took ' + Math.round(ms / 1000) + ' s on this device.');
  }
  function snapshotClean() {
    if (machines.some(function (m) { return m.resumed; })) return;   // only a fresh scenario is "clean"
    // a snapshot costs ~45 MB per VM in memory: keep it on roomy devices; small phones cold-boot on reset instead
    var dm = navigator.deviceMemory, mobile = /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent);
    if (dm ? dm < 4 && MULTI : (mobile && MULTI)) return;
    Promise.all(machines.map(function (m) { return m.emu.save_state(); })).then(function (bufs) {
      cleanSnap = { disks: {} }; machines.forEach(function (m, i) { cleanSnap[m.name] = bufs[i]; if (m.disk) cleanSnap.disks[m.name] = m.disk.slice(0); });
    }).catch(function () { cleanSnap = null; });
  }
  $('vmBoot').addEventListener('click', function () { start(null); });

  /* weak devices: offer the simulated version of the same skills */
  function showWeak(why) {
    var w = $('vmWeak'); if (!w) return;
    w.hidden = false;
    var t = w.querySelector('.why'); if (t) t.textContent = why + ' ';
  }
  (function advise() {
    var dm = navigator.deviceMemory, need = machines.length;
    if ((dm && dm <= 2 && need > 1) || (dm && dm < 2) || typeof WebAssembly !== 'object') showWeak(typeof WebAssembly !== 'object' ? 'This browser cannot run WebAssembly.' : 'This device reports little memory (' + dm + ' GB).');
  })();

  /* ---------------------------------------------------------------- grading */
  function readResult(m, tries) {
    return m.emu.read_file('/.ciwt-result').then(function (u8) {
      var t = new TextDecoder().decode(u8);
      if (!/\nend\s*$/.test(t)) throw new Error('partial');
      return t;
    }).catch(function () {
      if (tries <= 0) throw new Error('The VM ' + m.label + ' did not answer the check (is a program still running? press Ctrl-C).');
      return new Promise(function (r) { setTimeout(r, 150); }).then(function () { return readResult(m, tries - 1); });
    });
  }
  $('vmCheck').addEventListener('click', function () {
    var btn = this;
    if (!allReady) return;
    var busy = machines.filter(function (m) { return !m.idle(); });
    if (busy.length) { fb.className = 'lab-feedback bad mt-2'; fb.textContent = 'Finish the current command on ' + busy.map(function (m) { return m.label; }).join(' and ') + ' first (the prompt must be showing), or press Ctrl-C.'; if (wrap.classList.contains('term-focus')) kit.note('Not checked yet', [fb.textContent], 'bad'); return; }
    btn.disabled = true; fb.className = 'lab-feedback mt-2'; fb.textContent = 'Checking inside the VM' + (MULTI ? 's' : '') + '…';
    var t1 = performance.now(), probes = {};
    postLog().then(function () { return fetch(cfg.urls.probe, { credentials: 'same-origin' }); }).then(function (r) { return r.json(); }).then(function (j) {
      var scripts = j.scripts || { }; if (!j.scripts) scripts[machines[0].name] = j.script;
      return machines.reduce(function (p, m) {
        return p.then(function () {
          if (!scripts[m.name]) return;
          return m.hidden('.ciwt-probe', scripts[m.name], 'sh').then(function () { return readResult(m, 40); }).then(function (t) { probes[m.name] = t; });
        });
      }, Promise.resolve());
    }).then(function () {
      return kit.post(cfg.urls.vmcheck, { probes: probes, fabric: services ? { events: services.events.slice(-200) } : null });
    }).then(function (p) {
      kit.apply(p);
      var r = p.result || {};
      var ms = Math.round(performance.now() - t1);
      if (wrap.classList.contains('term-focus')) {   // phone full-screen terminal: every message, inside the terminal (r5)
        if (r.error) kit.note('Check could not finish', [r.error], 'bad');
        else if (p.complete) kit.note('✓ All checks passed (' + ms + ' ms)', [p.success_msg || 'Lab complete.'], 'ok', 'Tap Done to see your objectives.');
        else kit.note('Not yet — the VM' + (MULTI ? 's show' : ' shows') + ':', r.messages || ['A check is not met yet.'], 'bad');
      }
      if (r.error) { fb.className = 'lab-feedback bad mt-2'; fb.textContent = r.error; }
      else if (p.complete) { fb.className = 'lab-feedback ok mt-2'; fb.textContent = 'All checks passed (' + ms + ' ms).'; saveVM(true); }
      else {
        fb.className = 'lab-feedback bad mt-2';
        fb.innerHTML = '';
        var ul = document.createElement('ul'); ul.className = 'mb-0';
        (r.messages || []).forEach(function (msg) { var li = document.createElement('li'); li.textContent = msg; ul.appendChild(li); });
        fb.appendChild(document.createTextNode('Not yet — the VM' + (MULTI ? 's show' : ' shows') + ':')); fb.appendChild(ul);
      }
    }).catch(function (e) {
      machines.forEach(function (m) { if (m.suppress) { m.suppress.done = true; m.endSuppress(); } });
      fb.className = 'lab-feedback bad mt-2'; fb.textContent = e.message || 'Check failed — try again.';
      if (wrap.classList.contains('term-focus')) kit.note('Check could not finish', [fb.textContent], 'bad');
    }).then(function () { btn.disabled = false; });
  });

  /* ---------------------------------------------------------------- save / resume on this device (IndexedDB) */
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
    if (!allReady) return;
    var t = performance.now();
    Promise.all(machines.map(function (m) { return m.emu.save_state(); })).then(function (bufs) {
      var rec = { v: 2, machines: {}, disks: {}, net: services ? services.snapshot() : null, at: Date.now() }, size = 0;
      machines.forEach(function (m, i) { rec.machines[m.name] = bufs[i]; size += bufs[i].byteLength; if (m.disk) { rec.disks[m.name] = m.disk.slice(0); size += m.disk.byteLength; } });
      return idbDo('readwrite', function (s) { s.delete(DBKEY); return s.put(rec, DBKEY); }).then(function () {
        if (!quiet) kit.toast('Saved on this device (' + Math.round(size / 1048576) + ' MB, ' + Math.round(performance.now() - t) + ' ms). Resume it from this page later.', 'ok');
      });
    }).catch(function (e) { if (!quiet) kit.toast('Could not save: ' + e.message, 'bad'); });
  }
  $('vmSave').addEventListener('click', function () { saveVM(false); });
  $('vmRestart').addEventListener('click', function () {
    if (!window.confirm('Reset the VM' + (MULTI ? 's' : '') + ' to the start of the scenario? Changes inside are lost (your lab progress and objectives are kept).')) return;
    if (cleanSnap) {
      var btn = this; btn.disabled = true;
      machines.forEach(function (m) { if (m.disk && cleanSnap.disks[m.name]) new Uint8Array(m.disk).set(new Uint8Array(cleanSnap.disks[m.name])); });
      Promise.all(machines.map(function (m) { return m.emu.restore_state(cleanSnap[m.name]); })).then(function () {
        if (services) { services.leases = {}; services.arp = {}; services.events = []; }
        machines.forEach(function (m) { m.clearScreen(); m.hist = []; m.send('\n'); });
        kit.toast('Back to the start of the scenario.', 'ok');
      }).catch(function (e) { kit.toast('Reset failed: ' + e.message, 'bad'); }).then(function () { btn.disabled = false; });
      return;
    }
    machines.forEach(function (m) { if (m.emu) { m.emu.stop(); m.emu.destroy && m.emu.destroy(); } m.emu = null; m.booted = m.ready = false; m.clearScreen(); });
    $('vmTools').hidden = true; start(null);
  });
  idbDo('readonly', function (s) { return s.get(DBKEY); }).then(function (rec) {
    if (!rec || !$('vmResume')) return;
    if (rec instanceof ArrayBuffer) { var o = {}; o[machines[0].name] = rec; rec = { v: 2, machines: o }; }
    if (!machines.every(function (m) { return rec.machines && rec.machines[m.name]; })) return;
    $('vmResume').hidden = false;
    if (rec.at) $('vmResume').title = 'Saved ' + new Date(rec.at).toLocaleString();
    $('vmResume').addEventListener('click', function () { start(rec); });
  }).catch(function () {});

  /* ---------------------------------------------------------------- focus mode (phones), shared look with the simulator terminal */
  var narrow = window.matchMedia('(max-width: 699px)');
  var vv = window.visualViewport;
  function fit() {
    if (!wrap.classList.contains('term-focus')) return;
    var h = vv ? vv.height : innerHeight;
    wrap.style.setProperty('--vvh', h + 'px'); wrap.style.setProperty('--vvtop', (vv ? vv.offsetTop : 0) + 'px');
    wrap.classList.toggle('term-short', h < 560);   // keyboard open: drop the chips row so the prompt and keys stay visible
    active.screenEl.scrollTop = active.screenEl.scrollHeight;
  }
  function enterFocus() { wrap.classList.add('term-focus'); document.documentElement.classList.add('term-focus-on'); $('btnFocus').setAttribute('aria-pressed', 'true'); fit(); }
  function exitFocus() { wrap.classList.remove('term-focus', 'term-short'); document.documentElement.classList.remove('term-focus-on'); $('btnFocus').setAttribute('aria-pressed', 'false'); var n = $('termNote'); if (n) n.hidden = true; input.blur(); }
  window.addEventListener('orientationchange', function () { setTimeout(fit, 250); });
  if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
  input.addEventListener('focus', function () { if (narrow.matches) enterFocus(); });
  $('btnFocus').addEventListener('click', function () { if (wrap.classList.contains('term-focus')) exitFocus(); else { enterFocus(); input.focus(); } });
  $('btnFocusExit').addEventListener('click', exitFocus);
  window.addEventListener('beforeunload', function () {
    if (logQ.length && navigator.sendBeacon) { /* best effort: the next check re-posts anything queued */ postLog(); }
  });
})();
