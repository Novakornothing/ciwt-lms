/* Hardware workbench + RJ-45 cable bench (Option B pass 1). Client-side practice; the lab's own objectives are unchanged. */
(function () {
  'use strict';
  var root = document.getElementById('hwBench');
  if (!root) return;
  var msg = document.getElementById('hwbMsg');
  var NS = 'http://www.w3.org/2000/svg';
  function say(t, ok) { msg.textContent = t; msg.className = 'small mb-0 hwb-msg ' + (ok ? 'hwb-good' : 'hwb-bad'); }
  function el(tag, a, txt) { var e = document.createElementNS(NS, tag); for (var k in a) e.setAttribute(k, a[k]); if (txt) e.textContent = txt; return e; }

  if (root.dataset.mode === 'board') {
    var SLOTS = [
      {id: 'cpu', x: 120, y: 30, w: 70, h: 60, label: 'CPU socket (AM5 / LGA1700)'},
      {id: 'cooler', x: 120, y: 95, w: 70, h: 14, label: 'Cooler mount + CPU_FAN'},
      {id: 'dimm', x: 210, y: 25, w: 50, h: 85, label: 'DDR5 A2 / B2'},
      {id: 'pcie', x: 30, y: 150, w: 200, h: 14, label: 'PCIe x16 (top)'},
      {id: 'm2', x: 30, y: 125, w: 120, h: 12, label: 'M.2 2280 + standoff'},
      {id: 'atx24', x: 275, y: 40, w: 25, h: 80, label: '24-pin ATX'},
      {id: 'eps', x: 30, y: 20, w: 50, h: 16, label: '8-pin EPS'},
      {id: 'fp', x: 230, y: 200, w: 60, h: 14, label: 'Front-panel header'}];
    var PARTS = [
      {id: 'cpu', name: 'CPU (matching socket)', tip: 'Align the triangle / notch: no force, the lever closes the socket.'},
      {id: 'cooler', name: 'Cooler + thermal paste', tip: 'Thin, even paste; fan cable on CPU_FAN so firmware reads RPM.'},
      {id: 'dimm', name: '2 × DDR5 DIMMs', tip: 'Keyed notch: DDR5 only fits DDR5. Use A2 + B2 for dual channel.'},
      {id: 'pcie', name: 'Graphics card', tip: 'Top PCIe x16 slot, latch clicks, then PCIe power.'},
      {id: 'm2', name: 'NVMe SSD (M.2 2280)', tip: 'Move the standoff to the 2280 hole first, insert at 30°, screw down.'},
      {id: 'atx24', name: '24-pin ATX cable', tip: 'Keyed clip faces the latch; powers the board.'},
      {id: 'eps', name: '8-pin EPS cable', tip: 'CPU power near the socket: without it, no POST or instant off.'},
      {id: 'fp', name: 'Front-panel leads', tip: 'Match PWR_SW / RESET / LED+ / LED− to the manual; wrong pins make a good PC look dead.'}];
    var svg = document.getElementById('hwbSvg'), parts = document.getElementById('hwbParts'), pick = null, placed = {};
    svg.appendChild(el('rect', {x: 10, y: 10, width: 300, height: 220, rx: 8, 'class': 'hwb-board'}));
    SLOTS.forEach(function (s) {
      var g = el('g', {'class': 'hwb-slot', tabindex: 0, role: 'button', 'aria-label': s.label, 'data-slot': s.id});
      g.appendChild(el('rect', {x: s.x, y: s.y, width: s.w, height: s.h, rx: 3}));
      g.appendChild(el('text', {x: s.x + 2, y: s.y - 2, 'class': 'hwb-slot-label'}, s.label));
      function drop() {
        if (!pick) { say('Pick a part first.', false); return; }
        if (pick.id !== s.id) { say('✗ ' + pick.name + ' does not fit the ' + s.label + ' (wrong slot or keying).', false); return; }
        if (s.id === 'cooler' && !placed.cpu) { say('✗ Fit the CPU before the cooler.', false); return; }
        placed[s.id] = true; g.classList.add('hwb-filled');
        say('✓ ' + pick.name + ': ' + pick.tip + (Object.keys(placed).length === SLOTS.length ? ' Build complete: ready for first POST.' : ''), true);
        pick = null;
      }
      g.addEventListener('click', drop);
      g.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); drop(); } });
      svg.appendChild(g);
    });
    PARTS.forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'btn btn-sm btn-outline-navy'; b.textContent = p.name;
      b.addEventListener('click', function () { pick = p; say('Selected: ' + p.name + '. Now click its slot.', true); });
      parts.appendChild(b);
    });
    return;
  }

  var COLORS = ['white/orange', 'orange', 'white/green', 'blue', 'white/blue', 'green', 'white/brown', 'brown'];
  var B = COLORS.slice(), A = ['white/green', 'green', 'white/orange', 'blue', 'white/blue', 'orange', 'white/brown', 'brown'];
  var ends = document.getElementById('hwbEnds'), sel = [[], []];
  [0, 1].forEach(function (e) {
    var box = document.createElement('fieldset'); box.className = 'hwb-end';
    var lg = document.createElement('legend'); lg.className = 'small fw-bold'; lg.textContent = e ? 'End B (switch / patch panel)' : 'End A (PC)';
    box.appendChild(lg);
    for (var p = 0; p < 8; p++) {
      var lab = document.createElement('label'); lab.className = 'small hwb-pin';
      lab.textContent = 'Pin ' + (p + 1) + ' ';
      var s = document.createElement('select'); s.className = 'form-select form-select-sm';
      s.setAttribute('aria-label', (e ? 'End B' : 'End A') + ' pin ' + (p + 1));
      COLORS.concat(['(empty)']).forEach(function (c) { var o = document.createElement('option'); o.value = c; o.textContent = c; s.appendChild(o); });
      s.value = '(empty)'; lab.appendChild(s); box.appendChild(lab); sel[e].push(s);
    }
    ends.appendChild(box);
  });
  root.querySelectorAll('[data-fill]').forEach(function (b) {
    b.addEventListener('click', function () {
      var std = b.dataset.fill === 'A568A' ? A : B;
      sel[+b.dataset.end].forEach(function (s, i) { s.value = std[i]; });
    });
  });
  function same(x, y) { return x.every(function (v, i) { return v === y[i]; }); }
  document.getElementById('hwbTest').addEventListener('click', function () {
    var a = sel[0].map(function (s) { return s.value; }), b = sel[1].map(function (s) { return s.value; });
    var map = [], open = [];
    a.forEach(function (c, i) { var j = b.indexOf(c); if (c === '(empty)' || j < 0) open.push(i + 1); else map.push(i + 1 + '→' + (j + 1)); });
    if (open.length) return say('✗ Open on pin(s) ' + open.join(', ') + ': no continuity. Re-terminate that end. Wiremap: ' + map.join(' '), false);
    var std = function (x) { return same(x, B) ? 'T568B' : same(x, A) ? 'T568A' : null; };
    var sa = std(a), sb = std(b);
    if (sa && sb && sa === sb) return say('✓ Straight-through (' + sa + ' both ends): pins 1→1 … 8→8. Link up at 1 Gb/s.', true);
    if (sa && sb) return say('✓ Crossover (T568A ↔ T568B): 1↔3, 2↔6. Works PC-to-PC; Auto-MDI-X makes it link on modern switches too.', true);
    if (same(a, b)) return say('✗ Split pair: pins match end to end but not a standard order, so pairs are untwisted across 3/6. Continuity passes, link fails or errors under load. Re-terminate as T568B.', false);
    say('✗ Miswired / non-standard: ' + map.join(' ') + '. Re-terminate both ends to the same standard.', false);
  });
})();
