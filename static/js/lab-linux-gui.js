/* Live Linux desktop: restore a v86 snapshot (or boot the image) and grade through the serial shell. */
(function () {
  'use strict';
  var cfg = LabKit.config();
  var kit = LabKit.init(cfg);
  var V = cfg.vm || {};
  var $ = function (id) { return document.getElementById(id); };
  var status = $('lguiStatus'), bar = $('lguiBar'), fb = $('lguiFeedback'), perf = $('lguiPerf');
  var screen = $('lguiScreen');
  var PROMPT = /[#%$] $/;
  var emu = null, serial = '', ready = false, t0 = 0, clean = null;

  function setStatus(t, pct) {
    if (status) status.textContent = t;
    if (pct !== undefined && bar) {
      bar.style.width = pct + '%';
      bar.parentNode.setAttribute('aria-valuenow', Math.round(pct));
    }
  }
  function smallScreen() {
    var n = $('lguiSmall');
    if (!n) return;
    n.hidden = !(window.innerWidth < 900 || window.innerHeight < 520);
  }
  smallScreen();
  window.addEventListener('resize', smallScreen);

  function gunzip(buf) {
    if (typeof DecompressionStream !== 'function') return Promise.reject(new Error('This browser cannot unpack the desktop snapshot.'));
    var ds = new DecompressionStream('gzip');
    return new Response(new Blob([buf]).stream().pipeThrough(ds)).arrayBuffer();
  }
  var CACHE = 'novak-desktop-v1';
  function readBody(r, onprog) {
    var total = +r.headers.get('content-length') || 0, got = 0, chunks = [];
    var reader = r.body.getReader();
    function step() {
      return reader.read().then(function (x) {
        if (x.done) {
          var len = chunks.reduce(function (a, c) { return a + c.length; }, 0);
          var out = new Uint8Array(len), o = 0;
          chunks.forEach(function (c) { out.set(c, o); o += c.length; });
          return out.buffer;
        }
        chunks.push(x.value); got += x.value.length;
        if (onprog) onprog(got, total);
        return step();
      });
    }
    return step();
  }
  function loadPart(url, onprog) {
    var open = window.caches ? caches.open(CACHE) : Promise.resolve(null);
    return open.then(function (cache) {
      var hit = cache ? cache.match(url) : Promise.resolve(null);
      return Promise.resolve(hit).then(function (cached) {
        if (cached) {
          return cached.arrayBuffer().then(function (buf) {
            if (onprog) onprog(buf.byteLength, buf.byteLength);
            return buf;
          });
        }
        return fetch(url, { credentials: 'same-origin' }).then(function (r) {
          if (!r.ok) throw new Error('download failed');
          return readBody(r, onprog).then(function (buf) {
            if (cache) cache.put(url, new Response(buf.slice(0), { headers: { 'Content-Type': 'application/gzip' } }));
            return buf;
          });
        });
      });
    });
  }
  // Progress counts compressed bytes fetched (what the network actually moves), not the unpacked size.
  function loadParts(urls, onprog, sizes) {
    var pieces = [], doneNet = 0;
    var planned = (sizes || []).reduce(function (a, b) { return a + (+b || 0); }, 0);
    function next(i) {
      if (i >= urls.length) {
        var len = pieces.reduce(function (a, b) { return a + b.byteLength; }, 0);
        var out = new Uint8Array(len), o = 0;
        pieces.forEach(function (b) { out.set(new Uint8Array(b), o); o += b.byteLength; });
        return Promise.resolve(out.buffer);
      }
      var known = planned;
      return loadPart(urls[i], function (got, total) {
        if (!planned && total) known = Math.max(known, doneNet + total);
        if (onprog) onprog(doneNet + got, Math.max(known, doneNet + got));
      }).then(function (buf) {
        doneNet += buf.byteLength;
        if (!planned) known = Math.max(known, doneNet);
        if (onprog) onprog(doneNet, Math.max(planned || known, doneNet));
        return gunzip(buf);
      }).then(function (buf) {
        pieces[i] = buf;
        return next(i + 1);
      });
    }
    return next(0);
  }

  function waitPrompt(ms) {
    return new Promise(function (res, rej) {
      var st = Date.now(), quiet = 0;
      var iv = setInterval(function () {
        var lines = serial.split('\n');
        var last = lines[lines.length - 1];
        if (PROMPT.test(last)) {
          quiet += 30;
          if (quiet >= 120) { clearInterval(iv); res(); }
        } else quiet = 0;
        if (Date.now() - st > (ms || 20000)) { clearInterval(iv); rej(new Error('The desktop shell did not answer.')); }
      }, 30);
    });
  }
  function send(s) { if (emu) emu.serial0_send(s); }
  function runHidden(file, text, how) {
    serial = '';
    return emu.create_file('/' + file, new TextEncoder().encode(text)).then(function () {
      send(' ' + how + ' /mnt/' + file + '; rm -f /mnt/' + file + '\n');
      return waitPrompt(60000);
    });
  }

  function boot(stateBuf) {
    var mem = (V.memory_mb || 192) * 1024 * 1024;
    var vga = (V.vga_mb || 8) * 1024 * 1024;
    var opts = {
      wasm_path: cfg.assets.wasm,
      memory_size: mem,
      vga_memory_size: vga,
      bios: { url: cfg.assets.bios },
      vga_bios: { url: cfg.assets.vga_bios },
      screen_container: screen,
      filesystem: {},
      autostart: true,
      disable_speaker: true,
      cmdline: V.cmdline || 'console=ttyS0'
    };
    if (stateBuf) opts.initial_state = { buffer: stateBuf };
    else opts.bzimage = { url: cfg.assets.bzimage };
    emu = new window.V86(opts);
    emu.add_listener('serial0-output-byte', function (b) {
      serial += String.fromCharCode(b);
      if (serial.length > 8000) serial = serial.slice(-4000);
    });
    return new Promise(function (res) { emu.add_listener('emulator-loaded', res); }).then(function () {
      setStatus('Opening the desktop…', 90);
      send('\n');
      return waitPrompt(stateBuf ? 15000 : 90000);
    });
  }

  function arm() {
    return fetch(cfg.urls.probe, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (j) {
      if (!j.setup) return;
      serial = '';
      return runHidden('.novak-setup', j.setup, '.').then(function () { serial = ''; });
    }).then(function () {
      ready = true;
      var ms = Math.round(performance.now() - t0);
      setStatus('Desktop ready in ' + (ms / 1000).toFixed(1) + ' s. Click it, then right-click for the menu.', 100);
      if (perf) perf.textContent = 'This device: desktop ' + (ms / 1000).toFixed(1) + ' s.';
      kit.post(cfg.urls.log, { lines: [], booted: true, boot_ms: ms, ua: navigator.userAgent }).then(function (p) { kit.apply(p); }).catch(function () {});
      if (emu && emu.save_state && !clean) emu.save_state().then(function (b) { clean = b; }).catch(function () {});
      setTimeout(function () { var p = $('lguiProgress'); if (p) p.hidden = true; }, 1200);
      screen.focus();
    });
  }

  function start() {
    t0 = performance.now();
    setStatus('Loading the emulator…', 3);
    var s = document.createElement('script');
    s.src = cfg.assets.lib;
    s.onload = function () {
      setStatus('Downloading the desktop…', 8);
      var urls = (cfg.assets && cfg.assets.parts) || [];
      if (!urls.length) {
        setStatus('The desktop snapshot is not on this server.', 0);
        return;
      }
      loadParts(urls, function (got, total) {
        var pct = total ? 8 + 78 * got / total : 20;
        var mb = (got / 1e6).toFixed(1);
        var of = total ? ' of ' + (total / 1e6).toFixed(1) : '';
        setStatus('Downloading the desktop — ' + mb + of + ' MB', pct);
      }, V.state_part_bytes).then(function (buf) {
        clean = buf.slice(0);
        return boot(buf);
      }).then(arm).catch(function (e) {
        setStatus('Could not start the desktop: ' + (e.message || e) + '. Try a current Chrome, Edge, Firefox, or Safari.', 0);
      });
    };
    s.onerror = function () { setStatus('The emulator script did not load.', 0); };
    document.head.appendChild(s);
  }

  function readResult(tries) {
    return emu.read_file('/.ciwt-result').then(function (u8) {
      var t = new TextDecoder().decode(u8);
      if (!/\nend\s*$/.test(t)) throw new Error('partial');
      return t;
    }).catch(function () {
      if (tries <= 0) throw new Error('The desktop did not answer the check. Wait a moment and press Check my work again.');
      return new Promise(function (r) { setTimeout(r, 150); }).then(function () { return readResult(tries - 1); });
    });
  }

  $('lguiCheck').addEventListener('click', function () {
    var btn = this;
    if (!ready) { kit.toast('The desktop is still starting.', 'bad'); return; }
    if (!PROMPT.test(serial) && serial.slice(-2) !== '% ' && !PROMPT.test(serial.slice(-80))) {
      /* the shell is idle if we are not in the middle of a hidden command; send a blank line to surface the prompt */
    }
    btn.disabled = true;
    fb.className = 'lab-feedback mt-2';
    fb.textContent = 'Checking the live system…';
    var t1 = performance.now();
    fetch(cfg.urls.probe, { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (j) {
      return runHidden('.ciwt-probe', j.script, 'sh').then(function () { return readResult(40); });
    }).then(function (probe) {
      return kit.post(cfg.urls.vmcheck, { probes: { vm: probe } });
    }).then(function (p) {
      kit.apply(p);
      var r = p.result || {};
      var ms = Math.round(performance.now() - t1);
      if (r.error) { fb.className = 'lab-feedback bad mt-2'; fb.textContent = r.error; }
      else if (p.complete) { fb.className = 'lab-feedback ok mt-2'; fb.textContent = 'All checks passed (' + ms + ' ms).'; }
      else {
        fb.className = 'lab-feedback bad mt-2';
        fb.textContent = '';
        var ul = document.createElement('ul');
        (r.messages || ['A check is not met yet.']).forEach(function (m) {
          var li = document.createElement('li'); li.textContent = m; ul.appendChild(li);
        });
        fb.appendChild(document.createTextNode('Not yet — the desktop shows:'));
        fb.appendChild(ul);
      }
    }).catch(function (e) {
      fb.className = 'lab-feedback bad mt-2';
      fb.textContent = e.message || 'Check failed.';
    }).then(function () { btn.disabled = false; });
  });

  /* On-screen keyboard. Printable text goes through v86; Enter and arrows are scancodes. */
  var keysEl = $('lguiKeys');
  var rows = ['1234567890', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm', ' '];
  rows.forEach(function (row) {
    for (var i = 0; i < row.length; i++) {
      var ch = row[i];
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'btn btn-sm btn-outline-navy';
      b.textContent = ch === ' ' ? 'Space' : ch;
      b.setAttribute('data-ch', ch);
      keysEl.appendChild(b);
    }
  });
  [['Enter', [0x1c, 0x9c]], ['Backspace', [0x0e, 0x8e]], ['Tab', [0x0f, 0x8f]], ['Esc', [0x01, 0x81]],
   ['↑', [0xe0, 0x48, 0xe0, 0xc8]], ['↓', [0xe0, 0x50, 0xe0, 0xd0]], ['←', [0xe0, 0x4b, 0xe0, 0xcb]], ['→', [0xe0, 0x4d, 0xe0, 0xcd]]
  ].forEach(function (pair) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'btn btn-sm btn-outline-navy';
    b.textContent = pair[0];
    b.setAttribute('data-scan', pair[1].join(','));
    keysEl.appendChild(b);
  });
  keysEl.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!emu || t.tagName !== 'BUTTON') return;
    if (t.getAttribute('data-ch') !== null) emu.keyboard_send_text(t.getAttribute('data-ch'));
    else if (t.getAttribute('data-scan')) emu.keyboard_send_scancodes(t.getAttribute('data-scan').split(',').map(Number));
    screen.focus();
  });
  $('lguiKeysToggle').addEventListener('click', function () {
    var on = keysEl.hidden;
    keysEl.hidden = !on;
    this.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  $('lguiRelease').addEventListener('click', function () {
    if (document.exitPointerLock) document.exitPointerLock();
    if (emu && emu.mouse_set_status) emu.mouse_set_status(false);
  });

  kit.on(function (p) {
    if (p && p.ok && emu && clean) {
      ready = false;
      setStatus('Resetting the desktop…', 50);
      $('lguiProgress').hidden = false;
      emu.restore_state(clean).then(function () {
        serial = '';
        send('\n');
        return waitPrompt(15000);
      }).then(arm).catch(function (e) { setStatus('Reset failed: ' + e.message, 0); });
    }
  });

  if (cfg.assets && cfg.assets.parts && cfg.assets.parts.length) start();
})();
