/* Novak LMS Try-It simulations. MIT-compatible.
   Copyright (c) 2026 Novak Learning
   Permission is granted, free of charge, to any person obtaining a copy of this software
   to deal in the software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
   the software, and to permit persons to whom the software is furnished to do so,
   subject to including this notice in all copies or substantial portions. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.NovakSims = api;
})(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this), function () {
  'use strict';

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function svgEl(tag, attrs) {
    var n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }
  function btn(label, key, pressed) {
    var b = el('button', { type: 'button', 'data-sim-key': key, class: 'sim-choice' }, label);
    if (pressed) b.setAttribute('aria-pressed', 'true');
    else b.setAttribute('aria-pressed', 'false');
    return b;
  }
  function sameList(a, b) {
    if (!a || !b || a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
    return true;
  }
  function teachHash(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return ('00000000' + (h >>> 0).toString(16)).slice(-8);
  }
  function teachShift(s) {
    return String(s).split('').map(function (ch) {
      var c = ch.charCodeAt(0);
      if (c >= 97 && c <= 122) return String.fromCharCode(97 + ((c - 97 + 3) % 26));
      if (c >= 65 && c <= 90) return String.fromCharCode(65 + ((c - 65 + 3) % 26));
      return ch;
    }).join('');
  }
  function ipInt(ip) {
    return String(ip).split('.').reduce(function (n, p) { return ((n << 8) + (parseInt(p, 10) & 255)) >>> 0; }, 0);
  }
  function fmtIp(n) {
    return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.');
  }
  function maskOf(prefix) {
    if (prefix <= 0) return 0;
    if (prefix >= 32) return 0xffffffff;
    return (0xffffffff << (32 - prefix)) >>> 0;
  }
  function subnetFacts(ip, prefix) {
    var ipn = ipInt(ip), mask = maskOf(prefix);
    var network = (ipn & mask) >>> 0;
    var broadcast = (network | (~mask >>> 0)) >>> 0;
    var hosts = prefix >= 31 ? (prefix === 32 ? 1 : 2) : Math.pow(2, 32 - prefix) - 2;
    var first = prefix >= 31 ? fmtIp(network) : fmtIp((network + 1) >>> 0);
    var last = prefix >= 31 ? fmtIp(broadcast) : fmtIp((broadcast - 1) >>> 0);
    return { network: fmtIp(network), broadcast: fmtIp(broadcast), hosts: hosts, first: first, last: last, mask: fmtIp(mask) };
  }
  function bitsToOctal(bits) {
    var out = '';
    for (var g = 0; g < 3; g++) {
      out += String((bits[g * 3] ? 4 : 0) + (bits[g * 3 + 1] ? 2 : 0) + (bits[g * 3 + 2] ? 1 : 0));
    }
    return out;
  }
  function octalToBits(oct) {
    var bits = [];
    String(oct).split('').forEach(function (d) {
      var n = parseInt(d, 10) || 0;
      bits.push(n & 4 ? 1 : 0, n & 2 ? 1 : 0, n & 1 ? 1 : 0);
    });
    return bits;
  }
  function symbolic(bits) {
    var chars = 'rwxrwxrwx';
    return bits.map(function (b, i) { return b ? chars[i] : '-'; }).join('');
  }
  function raidInfo(level, disks, size) {
    var n = disks, s = size;
    if (level === '0') return { usable: n * s, fault: 0 };
    if (level === '1') return { usable: s, fault: n - 1 };
    if (level === '5') return { usable: (n - 1) * s, fault: 1 };
    if (level === '6') return { usable: Math.max(0, (n - 2) * s), fault: 2 };
    return { usable: Math.floor(n / 2) * s, fault: 1 };
  }
  function normCmd(s) {
    return String(s || '').trim().replace(/\s+/g, ' ').toLowerCase();
  }

  function renderOrder(stage, state, paint, ariaPrefix) {
    var list = el('ol', { class: 'sim-order' });
    state.order.forEach(function (step, idx) {
      var li = el('li', {});
      li.appendChild(el('span', { class: 'sim-order-text' }, step));
      var up = btn('Up', 'up-' + idx);
      var down = btn('Down', 'down-' + idx);
      up.setAttribute('aria-label', (ariaPrefix || 'Move up') + ': ' + step);
      down.setAttribute('aria-label', 'Move down: ' + step);
      up.addEventListener('click', function () {
        if (idx < 1) return;
        var tmp = state.order[idx - 1];
        state.order[idx - 1] = state.order[idx];
        state.order[idx] = tmp;
        state._focus = 'up-' + (idx - 1);
        paint();
      });
      down.addEventListener('click', function () {
        if (idx >= state.order.length - 1) return;
        var tmp = state.order[idx + 1];
        state.order[idx + 1] = state.order[idx];
        state.order[idx] = tmp;
        state._focus = 'down-' + (idx + 1);
        paint();
      });
      var moves = el('span', { class: 'sim-moves' });
      moves.appendChild(up);
      moves.appendChild(down);
      li.appendChild(moves);
      list.appendChild(li);
    });
    stage.appendChild(list);
  }

  function renderChoices(stage, state, field, choices, paint, groupLabel) {
    var wrap = el('div', { class: 'sim-choices', role: 'group', 'aria-label': groupLabel || 'Choose one' });
    choices.forEach(function (choice) {
      var b = btn(choice, 'c-' + choice, state[field] === choice);
      b.addEventListener('click', function () {
        state[field] = choice;
        state._focus = 'c-' + choice;
        paint();
      });
      wrap.appendChild(b);
    });
    stage.appendChild(wrap);
  }

  function renderSort(stage, spec, state) {
    state.placed = state.placed || {};
    var list = el('ul', { class: 'sim-sort' });
    (spec.params.items || []).forEach(function (item) {
      var li = el('li', {});
      var id = 'sim-sort-' + item.id;
      var lab = el('label', { for: id }, item.text);
      var sel = el('select', { id: id, 'data-sim-key': 's-' + item.id, 'aria-label': 'Group for ' + item.text });
      sel.appendChild(el('option', { value: '' }, 'Choose…'));
      (spec.params.buckets || []).forEach(function (bucket) {
        var opt = el('option', { value: bucket }, bucket);
        if (state.placed[item.id] === bucket) opt.setAttribute('selected', 'selected');
        sel.appendChild(opt);
      });
      sel.value = state.placed[item.id] || '';
      sel.addEventListener('change', function () { state.placed[item.id] = sel.value; });
      li.appendChild(lab);
      li.appendChild(sel);
      list.appendChild(li);
    });
    stage.appendChild(list);
  }

  function sortOk(spec, state) {
    var items = spec.params.items || [];
    var goal = (spec.goal && spec.goal.items) || {};
    if (!items.length) return false;
    for (var i = 0; i < items.length; i++) {
      if ((state.placed || {})[items[i].id] !== goal[items[i].id]) return false;
    }
    return true;
  }

  var widgets = {
    subnet: {
      sample: function () {
        return { type: 'subnet', instruction: 'Set the prefix to /28, then read the network address.',
          params: { ip: '10.0.0.50', startPrefix: 16 }, goal: { prefix: 28 } };
      },
      initial: function (spec) { return { prefix: spec.params.startPrefix }; },
      solved: function (spec) { return { prefix: spec.goal.prefix }; },
      evaluate: function (spec, state) {
        var ok = state.prefix === spec.goal.prefix;
        var facts = subnetFacts(spec.params.ip, state.prefix);
        return { ok: ok, message: ok
          ? 'Prefix /' + state.prefix + ' is right. Network ' + facts.network + ', broadcast ' + facts.broadcast + ', ' + facts.hosts + ' hosts.'
          : 'Not yet. The mask is /' + state.prefix + ' (network ' + facts.network + '). Set it to /' + spec.goal.prefix + '.' };
      },
      render: function (stage, spec, state) {
        var facts = subnetFacts(spec.params.ip, state.prefix);
        var fig = svgEl('svg', { viewBox: '0 0 320 72', role: 'img', 'aria-label': 'Address ' + spec.params.ip + ' with prefix ' + state.prefix });
        fig.appendChild(svgEl('rect', { x: '4', y: '8', width: '312', height: '56', rx: '8', fill: '#e8f0fb', stroke: '#0b2a55' }));
        var cap = svgEl('text', { x: '160', y: '32', 'text-anchor': 'middle', 'font-size': '16', fill: '#0b2a55' });
        cap.textContent = spec.params.ip + ' / ' + state.prefix;
        fig.appendChild(cap);
        var sub = svgEl('text', { x: '160', y: '52', 'text-anchor': 'middle', 'font-size': '12', fill: '#0b2a55' });
        sub.textContent = 'mask ' + facts.mask;
        fig.appendChild(sub);
        stage.appendChild(fig);
        var sliderLab = el('label', { class: 'sim-row' }, 'Prefix length');
        var slider = el('input', { type: 'range', min: '0', max: '32', value: String(state.prefix), 'data-sim-key': 'prefix', 'aria-label': 'Prefix length', 'aria-valuemin': '0', 'aria-valuemax': '32', 'aria-valuenow': String(state.prefix), 'aria-valuetext': 'slash ' + state.prefix });
        sliderLab.appendChild(slider);
        stage.appendChild(sliderLab);
        var bits = el('div', { class: 'sim-bits', role: 'group', 'aria-label': 'Mask bits, most significant first' });
        for (var i = 0; i < 32; i++) {
          var on = i < state.prefix;
          var b = btn(on ? '1' : '0', 'bit-' + i, on);
          b.setAttribute('aria-label', 'Mask bit ' + (i + 1) + (on ? ', on' : ', off'));
          (function (bit) {
            b.addEventListener('click', function () { state.prefix = bit + 1; state._focus = 'bit-' + bit; });
          })(i);
          b.addEventListener('click', function () { /* paint via parent listener below */ });
          bits.appendChild(b);
        }
        stage.appendChild(bits);
        // Bit clicks need a repaint; attach after the nodes exist by rewriting listeners.
        Array.prototype.forEach.call(bits.querySelectorAll('button'), function (b, i) {
          b.addEventListener('click', function () {
            state.prefix = i + 1;
            state._focus = 'bit-' + i;
            stage._paint();
          });
        });
        slider.addEventListener('input', function () {
          state.prefix = parseInt(slider.value, 10) || 0;
          slider.setAttribute('aria-valuenow', String(state.prefix));
          slider.setAttribute('aria-valuetext', 'slash ' + state.prefix);
          var f = subnetFacts(spec.params.ip, state.prefix);
          cap.textContent = spec.params.ip + ' / ' + state.prefix;
          sub.textContent = 'mask ' + f.mask;
          read.textContent = 'Network ' + f.network + ' · broadcast ' + f.broadcast + ' · usable ' + f.first + '–' + f.last + ' (' + f.hosts + ')';
          Array.prototype.forEach.call(bits.querySelectorAll('button'), function (bitBtn, idx) {
            var on = idx < state.prefix;
            bitBtn.textContent = on ? '1' : '0';
            bitBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
            bitBtn.setAttribute('aria-label', 'Mask bit ' + (idx + 1) + (on ? ', on' : ', off'));
          });
        });
        var read = el('p', { class: 'sim-read' }, 'Network ' + facts.network + ' · broadcast ' + facts.broadcast + ' · usable ' + facts.first + '–' + facts.last + ' (' + facts.hosts + ')');
        stage.appendChild(read);
      }
    },
    osi: {
      sample: function () {
        return { type: 'osi', instruction: 'Step through encapsulation, then name the layer that adds the IP header.',
          params: { layers: ['Data', 'Segment', 'Packet', 'Frame', 'Bits'], choices: ['Transport', 'Network', 'Data Link'], answer: 'Network' },
          goal: { answer: 'Network' } };
      },
      initial: function () { return { step: 0, choice: '' }; },
      solved: function (spec) { return { step: spec.params.layers.length - 1, choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        var done = state.step >= spec.params.layers.length - 1;
        var ok = done && state.choice === spec.goal.answer;
        if (!done) return { ok: false, message: 'Step through every header first.' };
        if (!state.choice) return { ok: false, message: 'Choose the layer that adds the IP header.' };
        return { ok: ok, message: ok ? 'The IP header is added at the Network layer, around the segment.' : 'Not that layer. Watch which header appears when the unit becomes a packet.' };
      },
      render: function (stage, spec, state, paint) {
        var layers = spec.params.layers;
        var fig = svgEl('svg', { viewBox: '0 0 280 150', role: 'img', 'aria-label': 'Encapsulation step ' + (state.step + 1) + ' of ' + layers.length + ', ' + layers[state.step] });
        for (var i = state.step; i >= 0; i--) {
          var pad = (state.step - i) * 14;
          var rect = svgEl('rect', { x: String(20 + pad), y: String(16 + pad), width: String(240 - pad * 2), height: String(100 - pad * 2), rx: '6', fill: i === state.step ? '#fdf3d8' : '#e8f0fb', stroke: '#0b2a55' });
          fig.appendChild(rect);
        }
        var label = svgEl('text', { x: '140', y: '78', 'text-anchor': 'middle', 'font-size': '16', fill: '#0b2a55' });
        label.textContent = layers[state.step];
        fig.appendChild(label);
        stage.appendChild(fig);
        var nav = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Encapsulation steps' });
        var back = btn('Back', 'osi-back');
        var next = btn('Next header', 'osi-next');
        back.disabled = state.step === 0;
        next.disabled = state.step >= layers.length - 1;
        back.addEventListener('click', function () { if (state.step > 0) { state.step -= 1; state._focus = 'osi-back'; paint(); } });
        next.addEventListener('click', function () { if (state.step < layers.length - 1) { state.step += 1; state._focus = 'osi-next'; paint(); } });
        nav.appendChild(back);
        nav.appendChild(next);
        stage.appendChild(nav);
        renderChoices(stage, state, 'choice', spec.params.choices, paint, 'Which layer adds the IP header?');
      }
    },
    ports: {
      sample: function () {
        return { type: 'ports', instruction: 'Match each service to its well-known port, then check.',
          params: { pairs: [{ service: 'HTTPS', port: '443' }, { service: 'SSH', port: '22' }, { service: 'DNS', port: '53' }, { service: 'RDP', port: '3389' }] },
          goal: { pairs: { HTTPS: '443', SSH: '22', DNS: '53', RDP: '3389' } } };
      },
      initial: function () { return { placed: {} }; },
      solved: function (spec) { return { placed: Object.assign({}, spec.goal.pairs) }; },
      evaluate: function (spec, state) {
        var pairs = spec.params.pairs || [];
        var n = 0;
        pairs.forEach(function (p) { if ((state.placed || {})[p.service] === spec.goal.pairs[p.service]) n++; });
        var ok = n === pairs.length && pairs.length > 0;
        return { ok: ok, message: ok ? 'Every service is on its well-known port.' : n + ' of ' + pairs.length + ' match. Change the others and check again.' };
      },
      render: function (stage, spec, state) {
        state.placed = state.placed || {};
        var ports = [];
        (spec.params.pairs || []).forEach(function (p) { if (ports.indexOf(p.port) < 0) ports.push(p.port); });
        var list = el('ul', { class: 'sim-sort' });
        (spec.params.pairs || []).forEach(function (p) {
          var li = el('li', {});
          var id = 'sim-port-' + p.service;
          li.appendChild(el('label', { for: id }, p.service));
          var sel = el('select', { id: id, 'data-sim-key': 'p-' + p.service, 'aria-label': 'Port for ' + p.service });
          sel.appendChild(el('option', { value: '' }, 'Choose…'));
          ports.forEach(function (port) { sel.appendChild(el('option', { value: port }, port)); });
          sel.value = state.placed[p.service] || '';
          sel.addEventListener('change', function () { state.placed[p.service] = sel.value; });
          li.appendChild(sel);
          list.appendChild(li);
        });
        stage.appendChild(list);
      }
    },
    chmod: {
      sample: function () {
        return { type: 'chmod', instruction: 'Set the permission boxes to 754, then check.',
          params: { target: '754' }, goal: { octal: '754' } };
      },
      initial: function () { return { bits: [0, 0, 0, 0, 0, 0, 0, 0, 0] }; },
      solved: function (spec) { return { bits: octalToBits(spec.goal.octal) }; },
      evaluate: function (spec, state) {
        var oct = bitsToOctal(state.bits || []);
        var ok = oct === spec.goal.octal;
        return { ok: ok, message: ok
          ? 'Mode ' + oct + ' (' + symbolic(state.bits) + ') matches.'
          : 'Now ' + oct + ' (' + symbolic(state.bits) + '). The target is ' + spec.goal.octal + '.' };
      },
      render: function (stage, spec, state) {
        var names = ['owner read', 'owner write', 'owner execute', 'group read', 'group write', 'group execute', 'others read', 'others write', 'others execute'];
        var letters = ['r', 'w', 'x', 'r', 'w', 'x', 'r', 'w', 'x'];
        var grid = el('div', { class: 'sim-chmod', role: 'group', 'aria-label': 'Permission bits' });
        ['Owner', 'Group', 'Others'].forEach(function (who, g) {
          var col = el('fieldset', { class: 'sim-perm-col' });
          col.appendChild(el('legend', {}, who));
          for (var k = 0; k < 3; k++) {
            var i = g * 3 + k;
            var id = 'sim-bit-' + i;
            var row = el('div', { class: 'sim-perm' });
            var box = el('input', { type: 'checkbox', id: id, 'data-sim-key': 'chmod-' + i, 'aria-label': names[i] });
            var lab = el('label', { for: id }, letters[k]);
            if (state.bits[i]) box.checked = true;
            (function (idx, input) {
              input.addEventListener('change', function () {
                state.bits[idx] = input.checked ? 1 : 0;
                out.textContent = bitsToOctal(state.bits) + '  ' + symbolic(state.bits);
              });
            })(i, box);
            row.appendChild(box);
            row.appendChild(lab);
            col.appendChild(row);
          }
          grid.appendChild(col);
        });
        stage.appendChild(grid);
        var out = el('p', { class: 'sim-read' }, bitsToOctal(state.bits) + '  ' + symbolic(state.bits));
        stage.appendChild(out);
      }
    },
    raid: {
      sample: function () {
        return { type: 'raid', instruction: 'Choose the RAID level that survives one failure and keeps more than half the capacity.',
          params: { disks: 4, sizeTB: 2, levels: ['0', '1', '5', '6', '10'] }, goal: { level: '5' } };
      },
      initial: function () { return { level: '0' }; },
      solved: function (spec) { return { level: spec.goal.level }; },
      evaluate: function (spec, state) {
        var info = raidInfo(state.level, spec.params.disks, spec.params.sizeTB);
        var ok = state.level === spec.goal.level;
        return { ok: ok, message: ok
          ? 'RAID ' + state.level + ' keeps ' + info.usable + ' TB and survives ' + info.fault + ' disk failure.'
          : 'RAID ' + state.level + ' keeps ' + info.usable + ' TB and survives ' + info.fault + '. Try another level.' };
      },
      render: function (stage, spec, state, paint) {
        var info = raidInfo(state.level, spec.params.disks, spec.params.sizeTB);
        var fig = svgEl('svg', { viewBox: '0 0 320 70', role: 'img', 'aria-label': spec.params.disks + ' disks in RAID ' + state.level });
        for (var i = 0; i < spec.params.disks; i++) {
          var x = 12 + i * (300 / spec.params.disks);
          fig.appendChild(svgEl('rect', { x: String(x), y: '12', width: String(Math.max(18, 280 / spec.params.disks - 8)), height: '46', rx: '4', fill: '#e8f0fb', stroke: '#0b2a55' }));
        }
        stage.appendChild(fig);
        renderChoices(stage, state, 'level', spec.params.levels.map(function (n) { return n; }), paint, 'RAID level');
        // renderChoices compares state.level to the label. Levels are '0','1',... and buttons say that. Good.
        stage.appendChild(el('p', { class: 'sim-read' }, spec.params.disks + ' disks × ' + spec.params.sizeTB + ' TB · usable ' + info.usable + ' TB · survives ' + info.fault + ' failure' + (info.fault === 1 ? '' : 's')));
      }
    },
    pcbuild: {
      sample: function () {
        return { type: 'pcbuild', instruction: 'Seat the CPU, memory, storage, and power supply on the board.',
          params: { slots: ['CPU', 'RAM', 'Storage', 'PSU'], parts: ['CPU', 'RAM', 'Storage', 'PSU', 'GPU'] },
          goal: { slots: ['CPU', 'RAM', 'Storage', 'PSU'] } };
      },
      initial: function () { return { selected: '', placed: {} }; },
      solved: function (spec) {
        var placed = {};
        spec.goal.slots.forEach(function (s) { placed[s] = s; });
        return { selected: '', placed: placed };
      },
      evaluate: function (spec, state) {
        var slots = spec.goal.slots || [];
        var n = 0;
        slots.forEach(function (s) { if ((state.placed || {})[s] === s) n++; });
        var ok = n === slots.length;
        return { ok: ok, message: ok ? 'CPU, memory, storage, and power supply are seated.' : n + ' of ' + slots.length + ' required parts are in the right slot.' };
      },
      render: function (stage, spec, state, paint) {
        state.placed = state.placed || {};
        var fig = svgEl('svg', { viewBox: '0 0 320 88', role: 'img', 'aria-label': 'Motherboard with four slots' });
        fig.appendChild(svgEl('rect', { x: '4', y: '4', width: '312', height: '80', rx: '8', fill: '#e7f6ee', stroke: '#0d7a52' }));
        spec.params.slots.forEach(function (slot, i) {
          var x = 16 + (i % 4) * 76;
          fig.appendChild(svgEl('rect', { x: String(x), y: '28', width: '68', height: '40', rx: '4', fill: state.placed[slot] ? '#fdf3d8' : '#ffffff', stroke: '#0b2a55' }));
          var t = svgEl('text', { x: String(x + 34), y: '52', 'text-anchor': 'middle', 'font-size': '10', fill: '#0b2a55' });
          t.textContent = state.placed[slot] || slot;
          fig.appendChild(t);
        });
        stage.appendChild(fig);
        var slots = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Board slots' });
        spec.params.slots.forEach(function (slot) {
          var b = btn(state.placed[slot] ? slot + ': ' + state.placed[slot] : slot + ' empty', 'slot-' + slot, !!state.placed[slot]);
          b.setAttribute('aria-label', 'Slot ' + slot + (state.placed[slot] ? ', holding ' + state.placed[slot] : ', empty'));
          b.addEventListener('click', function () {
            if (!state.selected) return;
            Object.keys(state.placed).forEach(function (k) { if (state.placed[k] === state.selected) delete state.placed[k]; });
            state.placed[slot] = state.selected;
            state.selected = '';
            state._focus = 'slot-' + slot;
            paint();
          });
          b.addEventListener('dragover', function (e) { e.preventDefault(); });
          b.addEventListener('drop', function (e) {
            e.preventDefault();
            var part = e.dataTransfer.getData('text/plain');
            if (!part) return;
            Object.keys(state.placed).forEach(function (k) { if (state.placed[k] === part) delete state.placed[k]; });
            state.placed[slot] = part;
            state._focus = 'slot-' + slot;
            paint();
          });
          slots.appendChild(b);
        });
        stage.appendChild(slots);
        var tray = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Parts tray' });
        spec.params.parts.forEach(function (part) {
          var used = Object.keys(state.placed).some(function (k) { return state.placed[k] === part; });
          var b = btn(part, 'part-' + part, state.selected === part);
          b.setAttribute('aria-label', part + (used ? ', already seated' : ', in the tray'));
          b.setAttribute('draggable', 'true');
          b.addEventListener('click', function () { state.selected = part; state._focus = 'part-' + part; paint(); });
          b.addEventListener('dragstart', function (e) { e.dataTransfer.setData('text/plain', part); });
          tray.appendChild(b);
        });
        stage.appendChild(tray);
        stage.appendChild(el('p', { class: 'sim-note' }, state.selected ? 'Selected ' + state.selected + '. Activate a slot to seat it.' : 'Select a part, then activate its slot. You can also drag it.'));
      }
    },
    boot: {
      sample: function () {
        return { type: 'boot', instruction: 'Step through startup, then pick the stage that loads the kernel.',
          params: { stages: ['POST', 'UEFI', 'Bootloader', 'Kernel', 'Sign-in'], choices: ['POST', 'UEFI', 'Kernel'], answer: 'Kernel' },
          goal: { answer: 'Kernel' } };
      },
      initial: function () { return { step: 0, choice: '' }; },
      solved: function (spec) { return { step: spec.params.stages.length - 1, choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        var done = state.step >= spec.params.stages.length - 1;
        if (!done) return { ok: false, message: 'Step through the whole startup path first.' };
        if (state.choice !== spec.goal.answer) return { ok: false, message: 'Not that stage. The kernel is loaded after the bootloader.' };
        return { ok: true, message: 'The kernel stage is the one that loads the operating system.' };
      },
      render: function (stage, spec, state, paint) {
        var stages = spec.params.stages;
        var fig = svgEl('svg', { viewBox: '0 0 320 64', role: 'img', 'aria-label': 'Startup stage ' + stages[state.step] });
        stages.forEach(function (name, i) {
          var x = 8 + i * 62;
          fig.appendChild(svgEl('rect', { x: String(x), y: '16', width: '56', height: '32', rx: '6', fill: i === state.step ? '#fdf3d8' : (i < state.step ? '#e7f6ee' : '#ffffff'), stroke: '#0b2a55' }));
          var t = svgEl('text', { x: String(x + 28), y: '36', 'text-anchor': 'middle', 'font-size': '8', fill: '#0b2a55' });
          t.textContent = name;
          fig.appendChild(t);
        });
        stage.appendChild(fig);
        var nav = el('div', { class: 'sim-choices' });
        var back = btn('Back', 'boot-back');
        var next = btn('Next stage', 'boot-next');
        back.disabled = state.step === 0;
        next.disabled = state.step >= stages.length - 1;
        back.addEventListener('click', function () { if (state.step > 0) { state.step -= 1; state._focus = 'boot-back'; paint(); } });
        next.addEventListener('click', function () { if (state.step < stages.length - 1) { state.step += 1; state._focus = 'boot-next'; paint(); } });
        nav.appendChild(back);
        nav.appendChild(next);
        stage.appendChild(nav);
        renderChoices(stage, state, 'choice', spec.params.choices, paint, 'Which stage loads the kernel?');
      }
    },
    acl: {
      sample: function () {
        return { type: 'acl', instruction: 'Walk the packet down the list and say whether it is permitted.',
          params: { packet: 'TCP port 443 from 10.1.1.5', rules: ['permit tcp 10.0.0.0/8 any eq 443', 'deny ip any any'], answer: 'permit', why: 'The first rule matches this packet, so the later deny never runs.' },
          goal: { answer: 'permit' } };
      },
      initial: function () { return { cursor: 0, choice: '' }; },
      solved: function (spec) { return { cursor: spec.params.rules.length, choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        if ((state.cursor || 0) < spec.params.rules.length) return { ok: false, message: 'Step the packet through every rule first.' };
        if (state.choice !== spec.goal.answer) return { ok: false, message: 'Not that action. ' + spec.params.why };
        return { ok: true, message: 'Right. ' + spec.params.why };
      },
      render: function (stage, spec, state, paint) {
        var matchAt = spec.params.answer === 'permit' ? 0 : spec.params.rules.length - 1;
        var fig = svgEl('svg', { viewBox: '0 0 320 36', role: 'img', 'aria-label': 'Packet ' + spec.params.packet });
        fig.appendChild(svgEl('rect', { x: '8', y: '6', width: '304', height: '24', rx: '12', fill: '#fdf3d8', stroke: '#9a7a2c' }));
        var t = svgEl('text', { x: '160', y: '22', 'text-anchor': 'middle', 'font-size': '11', fill: '#5a4310' });
        t.textContent = spec.params.packet;
        fig.appendChild(t);
        stage.appendChild(fig);
        var list = el('ol', { class: 'sim-rules' });
        spec.params.rules.forEach(function (rule, i) {
          var seen = state.cursor > i;
          var hit = seen && i === matchAt;
          var li = el('li', { class: hit ? 'is-hit' : (seen ? 'is-seen' : '') }, (i + 1) + '. ' + rule + (hit ? ' ← first match' : ''));
          list.appendChild(li);
        });
        stage.appendChild(list);
        var step = btn(state.cursor >= spec.params.rules.length ? 'Walk complete' : 'Step packet', 'acl-step');
        step.disabled = state.cursor >= spec.params.rules.length;
        step.addEventListener('click', function () {
          if (state.cursor < spec.params.rules.length) { state.cursor += 1; state._focus = 'acl-step'; paint(); }
        });
        stage.appendChild(step);
        renderChoices(stage, state, 'choice', ['permit', 'deny'], paint, 'Is the packet permitted or denied?');
      }
    },
    dora: {
      sample: function () {
        return { type: 'dora', instruction: 'Arrange the DHCP messages into DORA order, then check.',
          params: { mode: 'dhcp', steps: ['Discover', 'Offer', 'Request', 'Acknowledge'], start: ['Acknowledge', 'Request', 'Offer', 'Discover'] },
          goal: { order: ['Discover', 'Offer', 'Request', 'Acknowledge'] } };
      },
      initial: function (spec) { return { order: spec.params.start.slice() }; },
      solved: function (spec) { return { order: spec.goal.order.slice() }; },
      evaluate: function (spec, state) {
        var ok = sameList(state.order, spec.goal.order);
        return { ok: ok, message: ok ? (spec.params.mode === 'dns' ? 'That is the resolver’s lookup order.' : 'That is Discover, Offer, Request, Acknowledge.') : 'Not yet. Move the steps, then check again.' };
      },
      render: function (stage, spec, state, paint) { renderOrder(stage, state, paint, 'Move earlier'); }
    },
    vlan: {
      sample: function () {
        return { type: 'vlan', instruction: 'Choose which port forwards this frame, then check.',
          params: { ports: [{ id: '1', vlan: '10', label: 'Port 1 · VLAN 10' }, { id: '2', vlan: '10', label: 'Port 2 · VLAN 10' }, { id: '3', vlan: '20', label: 'Port 3 · VLAN 20' }], frame: 'VLAN 10 frame, destination MAC is on port 2', choices: ['Port 2', 'Port 3', 'Flood every port'], answer: 'Port 2' },
          goal: { answer: 'Port 2' } };
      },
      initial: function () { return { choice: '' }; },
      solved: function (spec) { return { choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        if (!state.choice) return { ok: false, message: 'Choose a port first.' };
        var ok = state.choice === spec.goal.answer;
        return { ok: ok, message: ok ? 'The MAC is on port 2, and that port is in VLAN 10, so the frame goes there only.' : 'A frame stays inside its VLAN. Port 3 is a different VLAN, and the switch already knows the MAC.' };
      },
      render: function (stage, spec, state, paint) {
        var fig = svgEl('svg', { viewBox: '0 0 320 90', role: 'img', 'aria-label': 'Switch with three access ports' });
        fig.appendChild(svgEl('rect', { x: '90', y: '28', width: '140', height: '40', rx: '6', fill: '#e8f0fb', stroke: '#0b2a55' }));
        var mid = svgEl('text', { x: '160', y: '52', 'text-anchor': 'middle', 'font-size': '12', fill: '#0b2a55' });
        mid.textContent = 'Switch';
        fig.appendChild(mid);
        spec.params.ports.forEach(function (p, i) {
          var x = 36 + i * 100;
          fig.appendChild(svgEl('rect', { x: String(x), y: '8', width: '48', height: '16', rx: '3', fill: p.vlan === '10' ? '#e7f6ee' : '#fde8e8', stroke: '#0b2a55' }));
          var t = svgEl('text', { x: String(x + 24), y: '20', 'text-anchor': 'middle', 'font-size': '9', fill: '#0b2a55' });
          t.textContent = 'V' + p.vlan;
          fig.appendChild(t);
        });
        stage.appendChild(fig);
        stage.appendChild(el('p', { class: 'sim-note' }, spec.params.frame));
        renderChoices(stage, state, 'choice', spec.params.choices, paint, 'Where does the frame go?');
      }
    },
    troubleshoot: {
      sample: function () {
        return { type: 'troubleshoot', instruction: 'Put the troubleshooting steps in order, then check.',
          params: { mode: 'order', steps: ['Identify the symptom and who is affected', 'Pick one likely cause', 'Test that cause with one change', 'Verify the result and write it down'], start: ['Verify the result and write it down', 'Test that cause with one change', 'Pick one likely cause', 'Identify the symptom and who is affected'] },
          goal: { order: ['Identify the symptom and who is affected', 'Pick one likely cause', 'Test that cause with one change', 'Verify the result and write it down'] } };
      },
      initial: function (spec) {
        if (spec.params.mode === 'sort') return { placed: {} };
        return { order: (spec.params.start || []).slice() };
      },
      solved: function (spec) {
        if (spec.params.mode === 'sort') return { placed: Object.assign({}, spec.goal.items) };
        return { order: spec.goal.order.slice() };
      },
      evaluate: function (spec, state) {
        if (spec.params.mode === 'sort') {
          var ok = sortOk(spec, state);
          return { ok: ok, message: ok ? 'Every item is in the right group.' : 'Some items are in the wrong group. Change them and check again.' };
        }
        var ok = sameList(state.order, spec.goal.order);
        var n = 0;
        (state.order || []).forEach(function (s, i) { if (spec.goal.order[i] === s) n++; });
        return { ok: ok, message: ok ? 'That order matches the method.' : n + ' of ' + spec.goal.order.length + ' steps are in place. Move the others and check again.' };
      },
      render: function (stage, spec, state, paint) {
        if (spec.params.mode === 'sort') renderSort(stage, spec, state);
        else renderOrder(stage, state, paint, 'Move earlier');
      }
    },
    cable: {
      sample: function () {
        return { type: 'cable', instruction: 'Name the connector drawn here, then check.',
          params: { shape: 'rj45', caption: 'Eight gold contacts in a clear plastic clip', choices: ['RJ-45', 'LC', 'USB-C', 'HDMI', 'DB-9'], answer: 'RJ-45' },
          goal: { answer: 'RJ-45' } };
      },
      initial: function () { return { choice: '' }; },
      solved: function (spec) { return { choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        if (!state.choice) return { ok: false, message: 'Choose the connector name first.' };
        var ok = state.choice === spec.goal.answer;
        return { ok: ok, message: ok ? state.choice + ' matches the drawing.' : 'Not ' + state.choice + '. Look at the shape again.' };
      },
      render: function (stage, spec, state, paint) {
        var fig = svgEl('svg', { viewBox: '0 0 200 80', role: 'img', 'aria-label': spec.params.caption });
        var s = spec.params.shape;
        if (s === 'rj45') {
          fig.appendChild(svgEl('rect', { x: '40', y: '20', width: '120', height: '40', rx: '4', fill: '#e8f0fb', stroke: '#0b2a55' }));
          for (var i = 0; i < 8; i++) fig.appendChild(svgEl('rect', { x: String(52 + i * 13), y: '28', width: '6', height: '16', fill: '#c9a227' }));
        } else if (s === 'lc') {
          fig.appendChild(svgEl('rect', { x: '70', y: '18', width: '36', height: '44', rx: '4', fill: '#e7f6ee', stroke: '#0d7a52' }));
          fig.appendChild(svgEl('rect', { x: '108', y: '30', width: '18', height: '10', fill: '#0d7a52' }));
        } else if (s === 'usbc') {
          fig.appendChild(svgEl('rect', { x: '60', y: '28', width: '80', height: '28', rx: '14', fill: '#e8f0fb', stroke: '#0b2a55' }));
        } else if (s === 'hdmi') {
          fig.appendChild(svgEl('polygon', { points: '40,24 150,24 160,56 30,56', fill: '#fdf3d8', stroke: '#9a7a2c' }));
        } else {
          fig.appendChild(svgEl('path', { d: 'M50 20 H140 V60 H70 L50 48 Z', fill: '#e8f0fb', stroke: '#0b2a55' }));
          fig.appendChild(svgEl('circle', { cx: '90', cy: '40', r: '4', fill: '#0b2a55' }));
        }
        stage.appendChild(fig);
        stage.appendChild(el('p', { class: 'sim-note' }, spec.params.caption));
        renderChoices(stage, state, 'choice', spec.params.choices, paint, 'Connector name');
      }
    },
    shell: {
      sample: function () {
        return { type: 'shell', instruction: 'Run the safe command, read the output, then answer the check.',
          params: { expect: 'ipconfig', hint: 'ipconfig', commands: { ipconfig: 'Default Gateway . . . : 192.168.1.1', help: 'Safe commands: help, ipconfig' }, question: 'What is the default gateway?', choices: ['192.168.1.1', '10.0.0.1', '169.254.1.1'], answer: '192.168.1.1' },
          goal: { command: 'ipconfig', answer: '192.168.1.1' } };
      },
      initial: function () { return { ran: [], output: '', choice: '', draft: '' }; },
      solved: function (spec) { return { ran: [spec.goal.command], output: '', choice: spec.goal.answer, draft: '' }; },
      evaluate: function (spec, state) {
        var ran = (state.ran || []).indexOf(spec.goal.command) >= 0;
        if (!ran) return { ok: false, message: 'Run ' + spec.params.hint + ' first. This sandbox only runs the listed safe commands.' };
        if (state.choice !== spec.goal.answer) return { ok: false, message: 'Read the output, then answer: ' + spec.params.question };
        return { ok: true, message: 'That matches the simulated output.' };
      },
      render: function (stage, spec, state, paint) {
        var row = el('div', { class: 'sim-shell' });
        var input = el('input', { type: 'text', 'data-sim-key': 'cmd', 'aria-label': 'Command', placeholder: 'Try ' + spec.params.hint, value: state.draft || '' });
        input.value = state.draft || '';
        var run = btn('Run', 'run');
        run.addEventListener('click', function () {
          var cmd = normCmd(input.value);
          state.draft = '';
          if (!cmd || /[;|&$`<>]/.test(cmd) || !Object.prototype.hasOwnProperty.call(spec.params.commands, cmd)) {
            state.output = 'This sandbox only runs the listed safe commands. Try: ' + spec.params.hint;
          } else {
            if (state.ran.indexOf(cmd) < 0) state.ran.push(cmd);
            state.output = spec.params.commands[cmd];
          }
          state._focus = 'cmd';
          paint();
        });
        input.addEventListener('input', function () { state.draft = input.value; });
        input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); run.click(); } });
        row.appendChild(input);
        row.appendChild(run);
        stage.appendChild(row);
        stage.appendChild(el('pre', { class: 'sim-out' }, state.output || 'Output appears here.'));
        stage.appendChild(el('p', { class: 'sim-note' }, spec.params.question));
        renderChoices(stage, state, 'choice', spec.params.choices, paint, spec.params.question);
      }
    },
    cia: {
      sample: function () {
        return { type: 'cia', instruction: 'Classify each case as confidentiality, integrity, or availability.',
          params: { buckets: ['Confidentiality', 'Integrity', 'Availability'], items: [{ id: 'c0', text: 'A laptop is stolen from an unlocked desk.', bucket: 'Confidentiality' }, { id: 'c1', text: 'A ticket total was edited after the tech saved it.', bucket: 'Integrity' }, { id: 'c2', text: 'The file server is up but no one can reach it.', bucket: 'Availability' }, { id: 'c3', text: 'A password was pasted into a public chat.', bucket: 'Confidentiality' }] },
          goal: { items: { c0: 'Confidentiality', c1: 'Integrity', c2: 'Availability', c3: 'Confidentiality' } } };
      },
      initial: function () { return { placed: {} }; },
      solved: function (spec) { return { placed: Object.assign({}, spec.goal.items) }; },
      evaluate: function (spec, state) {
        var ok = sortOk(spec, state);
        return { ok: ok, message: ok ? 'Each case is in the right security goal.' : 'Some cases are in the wrong goal. Change them and check again.' };
      },
      render: function (stage, spec, state) { renderSort(stage, spec, state); }
    },
    hash: {
      sample: function () {
        return { type: 'hash', instruction: 'Change one character and confirm the teaching hash changes.',
          params: { start: 'backup-report' }, goal: { changed: true } };
      },
      initial: function (spec) { return { text: spec.params.start, cipher: false }; },
      solved: function (spec) { return { text: spec.params.start + '!', cipher: false }; },
      evaluate: function (spec, state) {
        var changed = String(state.text || '') !== spec.params.start && String(state.text || '').length > 0;
        var ok = changed && teachHash(state.text) !== teachHash(spec.params.start);
        return { ok: ok, message: ok ? 'One change produced a different teaching hash. A real digest is built for the same effect.' : 'Edit the text so it is not the original, then check.' };
      },
      render: function (stage, spec, state) {
        var lab = el('label', { class: 'sim-row' }, 'Message');
        var input = el('input', { type: 'text', 'data-sim-key': 'hash-text', 'aria-label': 'Message to hash', value: state.text });
        input.value = state.text;
        var out = el('p', { class: 'sim-read' }, '');
        function paintHash() {
          var digest = teachHash(state.text || '');
          var extra = state.cipher ? ' · teaching shift: ' + teachShift(state.text || '') : '';
          out.textContent = 'Teaching hash ' + digest + extra;
        }
        input.addEventListener('input', function () { state.text = input.value; paintHash(); });
        lab.appendChild(input);
        stage.appendChild(lab);
        var toggle = btn(state.cipher ? 'Hide teaching shift' : 'Show teaching shift', 'cipher', state.cipher);
        toggle.addEventListener('click', function () {
          state.cipher = !state.cipher;
          toggle.textContent = state.cipher ? 'Hide teaching shift' : 'Show teaching shift';
          toggle.setAttribute('aria-pressed', state.cipher ? 'true' : 'false');
          paintHash();
        });
        stage.appendChild(toggle);
        stage.appendChild(out);
        stage.appendChild(el('p', { class: 'sim-note' }, 'This is a teaching hash and a letter shift, not a digest or cipher you would deploy.'));
        paintHash();
      }
    },
    phish: {
      sample: function () {
        return { type: 'phish', instruction: 'Flag only the real phishing clues, then check.',
          params: { sender: 'billing@paypa1.example', subject: 'Account closes in 10 minutes', body: 'Confirm your password at secure-login.example.net.', clues: [{ id: 'domain', text: 'Sender domain is paypa1.example', real: true }, { id: 'logo', text: 'The message includes a logo', real: false }] },
          goal: { flags: ['domain'] } };
      },
      initial: function () { return { flags: {} }; },
      solved: function (spec) {
        var flags = {};
        (spec.goal.flags || []).forEach(function (id) { flags[id] = true; });
        return { flags: flags };
      },
      evaluate: function (spec, state) {
        var flags = state.flags || {};
        var want = (spec.goal.flags || []).slice().sort().join('|');
        var got = Object.keys(flags).filter(function (id) { return flags[id]; }).sort().join('|');
        var ok = got === want && want.length > 0;
        return { ok: ok, message: ok ? 'You flagged the real clues and left the decoys alone.' : 'Flag every real clue, and clear any clue that is normal.' };
      },
      render: function (stage, spec, state) {
        state.flags = state.flags || {};
        var card = el('div', { class: 'sim-mail' });
        card.appendChild(el('p', {}, 'From: ' + spec.params.sender));
        card.appendChild(el('p', {}, 'Subject: ' + spec.params.subject));
        card.appendChild(el('p', {}, spec.params.body));
        stage.appendChild(card);
        var list = el('div', { class: 'sim-clues', role: 'group', 'aria-label': 'Possible clues' });
        (spec.params.clues || []).forEach(function (clue) {
          var id = 'sim-clue-' + clue.id;
          var row = el('div', { class: 'sim-perm' });
          var box = el('input', { type: 'checkbox', id: id, 'data-sim-key': 'clue-' + clue.id, 'aria-label': clue.text });
          var lab = el('label', { for: id }, clue.text);
          if (state.flags[clue.id]) box.checked = true;
          box.addEventListener('change', function () { state.flags[clue.id] = box.checked; });
          row.appendChild(box);
          row.appendChild(lab);
          list.appendChild(row);
        });
        stage.appendChild(list);
      }
    },
    logs: {
      sample: function () {
        return { type: 'logs', instruction: 'Filter the lines and select the failed sign-in.',
          params: { lines: [{ id: 'l1', sev: 'info', src: 'kernel', text: 'eth0 link up' }, { id: 'l3', sev: 'error', src: 'auth', text: 'Failed sign-in for jlee' }], answerId: 'l3' },
          goal: { pick: 'l3' } };
      },
      initial: function () { return { filter: 'all', pick: '' }; },
      solved: function (spec) { return { filter: 'error', pick: spec.goal.pick }; },
      evaluate: function (spec, state) {
        var ok = state.pick === spec.goal.pick;
        return { ok: ok, message: ok ? 'That line is the failed sign-in.' : 'Select the failed sign-in line. The severity filter can hide the rest.' };
      },
      render: function (stage, spec, state, paint) {
        var filters = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Severity filter' });
        ['all', 'error', 'warning', 'info'].forEach(function (sev) {
          var b = btn(sev, 'f-' + sev, state.filter === sev);
          b.setAttribute('aria-label', 'Show ' + sev + ' lines');
          b.addEventListener('click', function () { state.filter = sev; state._focus = 'f-' + sev; paint(); });
          filters.appendChild(b);
        });
        stage.appendChild(filters);
        var list = el('div', { class: 'sim-logs', role: 'listbox', 'aria-label': 'Log lines' });
        (spec.params.lines || []).forEach(function (line) {
          if (state.filter !== 'all' && line.sev !== state.filter) return;
          var b = btn(line.sev + ' · ' + line.src + ' · ' + line.text, 'log-' + line.id, state.pick === line.id);
          b.setAttribute('aria-selected', state.pick === line.id ? 'true' : 'false');
          b.addEventListener('click', function () { state.pick = line.id; state._focus = 'log-' + line.id; paint(); });
          list.appendChild(b);
        });
        stage.appendChild(list);
      }
    },
    match: {
      sample: function () {
        return { type: 'match', instruction: 'Match each term to the group it belongs in, then check.',
          params: { buckets: ['Keep', 'Replace'], items: [
            { id: 'i0', text: 'Known-good cable', bucket: 'Keep' }, { id: 'i1', text: 'Swollen capacitor', bucket: 'Replace' },
            { id: 'i2', text: 'Current driver', bucket: 'Keep' }, { id: 'i3', text: 'Burned connector', bucket: 'Replace' }
          ] },
          goal: { items: { i0: 'Keep', i1: 'Replace', i2: 'Keep', i3: 'Replace' } } };
      },
      initial: function () { return { placed: {} }; },
      solved: function (spec) { return { placed: Object.assign({}, spec.goal.items) }; },
      evaluate: function (spec, state) {
        var ok = sortOk(spec, state);
        return { ok: ok, message: ok ? 'Every term is in the right group.' : 'Some terms are in the wrong group. Change them and check again.' };
      },
      render: function (stage, spec, state, paint) {
        state.placed = state.placed || {};
        var list = el('ul', { class: 'sim-sort' });
        (spec.params.items || []).forEach(function (item) {
          var li = el('li', {});
          li.appendChild(el('span', { class: 'sim-order-text' }, item.text));
          var picks = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Group for ' + item.text });
          (spec.params.buckets || []).forEach(function (bucket) {
            var b = btn(bucket, 'm-' + item.id + '-' + bucket, state.placed[item.id] === bucket);
            b.setAttribute('aria-label', item.text + ', ' + bucket);
            b.addEventListener('click', function () {
              state.placed[item.id] = bucket;
              state._focus = 'm-' + item.id + '-' + bucket;
              paint();
            });
            picks.appendChild(b);
          });
          li.appendChild(picks);
          list.appendChild(li);
        });
        stage.appendChild(list);
      }
    },
    pairs: {
      sample: function () {
        return { type: 'pairs', instruction: 'Sort one card at a time into the right pile, then check.',
          params: { buckets: ['Keep', 'Replace'], items: [
            { id: 'i0', text: 'Known-good cable', bucket: 'Keep' }, { id: 'i1', text: 'Swollen capacitor', bucket: 'Replace' },
            { id: 'i2', text: 'Current driver', bucket: 'Keep' }, { id: 'i3', text: 'Burned connector', bucket: 'Replace' }
          ] },
          goal: { items: { i0: 'Keep', i1: 'Replace', i2: 'Keep', i3: 'Replace' } } };
      },
      initial: function () { return { cursor: 0, placed: {} }; },
      solved: function (spec) { return { cursor: (spec.params.items || []).length, placed: Object.assign({}, spec.goal.items) }; },
      evaluate: function (spec, state) {
        var items = spec.params.items || [];
        if (Object.keys(state.placed || {}).length < items.length) return { ok: false, message: 'Place every card, then check.' };
        var ok = sortOk(spec, state);
        return { ok: ok, message: ok ? 'Every card is in the right pile.' : 'Some cards are in the wrong pile. Reset and try the missed ones again.' };
      },
      render: function (stage, spec, state, paint) {
        var items = spec.params.items || [];
        state.placed = state.placed || {};
        var done = state.cursor >= items.length;
        var item = done ? null : items[state.cursor];
        stage.appendChild(el('p', { class: 'sim-note' }, done ? 'Every card is placed.' : ('Card ' + (state.cursor + 1) + ' of ' + items.length)));
        if (item) {
          stage.appendChild(el('p', { class: 'sim-read' }, item.text));
          var picks = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Pile for ' + item.text });
          (spec.params.buckets || []).forEach(function (bucket) {
            var b = btn(bucket, 'p-' + bucket);
            b.setAttribute('aria-label', 'Place ' + item.text + ' in ' + bucket);
            b.addEventListener('click', function () {
              state.placed[item.id] = bucket;
              state.cursor += 1;
              state._focus = 'p-' + bucket;
              paint();
            });
            picks.appendChild(b);
          });
          stage.appendChild(picks);
        }
      }
    },
    classify: {
      sample: function () {
        return { type: 'classify', instruction: 'Sort each item into the matching group, then check.',
          params: { buckets: ['Input', 'Output', 'Both'], items: [
            { id: 'i0', text: 'Keyboard', bucket: 'Input' }, { id: 'i1', text: 'Printer', bucket: 'Output' },
            { id: 'i2', text: 'Touchscreen', bucket: 'Both' }, { id: 'i3', text: 'Speaker', bucket: 'Output' }
          ] },
          goal: { items: { i0: 'Input', i1: 'Output', i2: 'Both', i3: 'Output' } } };
      },
      initial: function () { return { placed: {} }; },
      solved: function (spec) { return { placed: Object.assign({}, spec.goal.items) }; },
      evaluate: function (spec, state) {
        var ok = sortOk(spec, state);
        return { ok: ok, message: ok ? 'Every item is in the right group.' : 'Some items are in the wrong group. Change them and check again.' };
      },
      render: function (stage, spec, state) { renderSort(stage, spec, state); }
    },
    sequence: {
      sample: function () {
        return { type: 'sequence', instruction: 'Put these steps in the order this concept uses, then check.',
          params: { steps: ['Name the symptom', 'Test one cause', 'Record the result'], start: ['Record the result', 'Test one cause', 'Name the symptom'] },
          goal: { order: ['Name the symptom', 'Test one cause', 'Record the result'] } };
      },
      initial: function (spec) { return { order: spec.params.start.slice() }; },
      solved: function (spec) { return { order: spec.goal.order.slice() }; },
      evaluate: function (spec, state) {
        var ok = sameList(state.order, spec.goal.order);
        return { ok: ok, message: ok ? 'That order matches this concept.' : 'Not yet. Move the steps, then check again.' };
      },
      render: function (stage, spec, state, paint) { renderOrder(stage, state, paint, 'Move earlier'); }
    },
    trace: {
      sample: function () {
        return { type: 'trace', instruction: 'Tap the steps in the order this concept uses, then check.',
          params: { steps: ['One', 'Two', 'Three', 'Four', 'Five'], start: ['Five', 'Four', 'Three', 'Two', 'One'] },
          goal: { order: ['One', 'Two', 'Three', 'Four', 'Five'] } };
      },
      initial: function (spec) { return { picked: [], pool: spec.params.start.slice() }; },
      solved: function (spec) { return { picked: spec.goal.order.slice(), pool: [] }; },
      evaluate: function (spec, state) {
        if ((state.picked || []).length < spec.goal.order.length) return { ok: false, message: 'Tap every step first.' };
        var ok = sameList(state.picked, spec.goal.order);
        return { ok: ok, message: ok ? 'That trace matches this concept.' : 'That order is off. Undo and tap the steps again.' };
      },
      render: function (stage, spec, state, paint) {
        var built = el('ol', { class: 'sim-order', 'aria-label': 'Steps you have chosen' });
        (state.picked || []).forEach(function (step, idx) {
          built.appendChild(el('li', {}, (idx + 1) + '. ' + step));
        });
        if (!(state.picked || []).length) built.appendChild(el('li', {}, 'Nothing chosen yet'));
        stage.appendChild(built);
        var undo = btn('Undo last', 'trace-undo');
        undo.disabled = !(state.picked || []).length;
        undo.addEventListener('click', function () {
          var last = state.picked.pop();
          if (last) state.pool.push(last);
          state._focus = 'trace-undo';
          paint();
        });
        stage.appendChild(undo);
        var pool = el('div', { class: 'sim-choices', role: 'group', 'aria-label': 'Remaining steps' });
        (state.pool || []).forEach(function (step, idx) {
          var b = btn(step, 't-' + idx);
          b.setAttribute('aria-label', 'Choose step: ' + step);
          b.addEventListener('click', function () {
            state.pool.splice(idx, 1);
            state.picked.push(step);
            paint();
          });
          pool.appendChild(b);
        });
        stage.appendChild(pool);
      }
    },
    choose: {
      sample: function () {
        return { type: 'choose', instruction: 'Pick the line that matches this concept, then check.',
          params: { stem: 'Which line is the safe habit?', options: ['Write the outcome in the ticket', 'Guess and reboot', 'Skip the note'], answer: 'Write the outcome in the ticket' },
          goal: { answer: 'Write the outcome in the ticket' } };
      },
      initial: function () { return { choice: '' }; },
      solved: function (spec) { return { choice: spec.goal.answer }; },
      evaluate: function (spec, state) {
        if (!state.choice) return { ok: false, message: 'Pick a line first.' };
        var ok = state.choice === spec.goal.answer;
        return { ok: ok, message: ok ? 'That line matches this concept.' : 'Not that line. Read the stem and pick again.' };
      },
      render: function (stage, spec, state, paint) {
        stage.appendChild(el('p', { class: 'sim-read' }, spec.params.stem));
        renderChoices(stage, state, 'choice', spec.params.options, paint, spec.params.stem);
      }
    }
  };

  // Subnet bit buttons call stage._paint, set in mount.
  var _subnetRender = widgets.subnet.render;
  widgets.subnet.render = function (stage, spec, state, paint) {
    stage._paint = paint;
    _subnetRender(stage, spec, state, paint);
  };

  function mount(node) {
    if (!node || node.getAttribute('data-sim-ready') === '1') return;
    var specEl = node.querySelector('.novak-sim-spec');
    var stage = node.querySelector('.novak-sim-stage');
    var fb = node.querySelector('.novak-sim-fb');
    if (!specEl || !stage) return;
    var spec;
    try { spec = JSON.parse(specEl.textContent || ''); } catch (e) { return; }
    var widget = widgets[spec.type];
    if (!widget) return;
    node.setAttribute('data-sim-ready', '1');
    var state = widget.initial(spec);
    function paint() {
      var key = state._focus || '';
      state._focus = '';
      stage.textContent = '';
      widget.render(stage, spec, state, paint);
      if (key) {
        var again = stage.querySelector('[data-sim-key="' + key + '"]');
        if (again && again.focus) again.focus({ preventScroll: true });
      }
    }
    paint();
    var check = node.querySelector('[data-sim-check]');
    var reset = node.querySelector('[data-sim-reset]');
    if (check) check.addEventListener('click', function () {
      var res = widget.evaluate(spec, state);
      if (fb) fb.textContent = res.message;
      var url = node.getAttribute('data-evidence-url');
      var fetchFn = typeof fetch === 'function' ? fetch : null;
      if (!url || !fetchFn) return;
      var tok = '';
      try { tok = (document.querySelector('meta[name="csrf-token"]') || {}).content || ''; } catch (err) { tok = ''; }
      var data = new FormData();
      data.set('kind', 'sim_check');
      data.set('correct', res.ok ? '1' : '0');
      data.set('answer', String(res.message || '').slice(0, 300));
      fetchFn(url, { method: 'POST', credentials: 'same-origin', body: data,
        headers: { 'X-Requested-With': 'fetch', Accept: 'application/json', 'X-CSRFToken': tok } }).catch(function () {});
    });
    if (reset) reset.addEventListener('click', function () {
      var fresh = widget.initial(spec);
      Object.keys(state).forEach(function (k) { delete state[k]; });
      Object.keys(fresh).forEach(function (k) { state[k] = fresh[k]; });
      if (fb) fb.textContent = '';
      paint();
    });
  }

  function mountAll(scope) {
    var rootEl = scope || (typeof document !== 'undefined' ? document : null);
    if (!rootEl || !rootEl.querySelectorAll) return;
    Array.prototype.forEach.call(rootEl.querySelectorAll('[data-novak-sim]'), mount);
  }

  return {
    TYPES: ['subnet', 'osi', 'ports', 'chmod', 'raid', 'pcbuild', 'boot', 'acl', 'dora', 'vlan', 'troubleshoot', 'cable', 'shell', 'cia', 'hash', 'phish', 'logs', 'match', 'pairs', 'classify', 'sequence', 'trace', 'choose'],
    sample: function (type) { return widgets[type].sample(); },
    initial: function (spec) { return widgets[spec.type].initial(spec); },
    solved: function (spec) { return widgets[spec.type].solved(spec); },
    evaluate: function (spec, state) { return widgets[spec.type].evaluate(spec, state); },
    subnetFacts: subnetFacts,
    raidInfo: raidInfo,
    bitsToOctal: bitsToOctal,
    teachHash: teachHash,
    mount: mount,
    mountAll: mountAll
  };
});
