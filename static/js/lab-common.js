/* Novak LMS live labs — shared client (all lab kinds).
 * State lives on the server (lab_progress). This file only renders what the server returns:
 * objectives, score, hints, undo/reset, toasts and graded steps (activity labs and checkpoints).
 * Works with mouse, touch and keyboard; no drag-only interactions. */
(function () {
  'use strict';

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'text') n.textContent = v;
      else if (k === 'html') n.innerHTML = v;
      else if (k === 'class') n.className = v;
      else if (k.slice(0, 2) === 'on' && typeof v === 'function') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : v);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }

  function Kit(cfg) {
    this.cfg = cfg;
    this.urls = cfg.urls;
    this.state = cfg.boot || {};
    this.handlers = [];
    this.live = document.getElementById('labLive');
    var self = this;
    var hb = document.getElementById('btnHint');
    if (hb) hb.addEventListener('click', function () { self.hint(); });
    var ub = document.getElementById('btnUndo');
    if (ub) ub.addEventListener('click', function () { self.undo(); });
    var rb = document.getElementById('btnReset');
    if (rb) rb.addEventListener('click', function () { self.reset(); });
    this.apply(this.state, true);
  }

  Kit.prototype.on = function (fn) { this.handlers.push(fn); };

  Kit.prototype.post = function (url, body) {
    var self = this;
    return fetch(url, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(body || {})
    }).then(function (r) {
      if (r.status === 401 || r.redirected) { throw new Error('signed-out'); }
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).catch(function (e) {
      self.toast(e.message === 'signed-out' ? 'Your session ended — sign in again. Your work so far is saved.'
        : 'Connection problem — that action was not saved. Check the connection and try again.', 'error');
      throw e;
    });
  };

  Kit.prototype.say = function (msg) {
    if (!this.live) return;
    this.live.textContent = '';
    var live = this.live;
    setTimeout(function () { live.textContent = msg; }, 30);
  };

  Kit.prototype.toast = function (msg, kind) {
    var box = document.getElementById('labToast');
    if (!box) return;
    box.textContent = msg;
    box.className = 'lab-toast show ' + (kind || '');
    clearTimeout(this._t);
    this._t = setTimeout(function () { box.className = 'lab-toast'; }, kind === 'error' ? 6000 : 3500);
  };

  Kit.prototype.apply = function (p, first) {
    if (!p) return;
    var prev = this.state || {};
    this.state = Object.assign({}, prev, p);
    var done = new Set(p.done || []);
    var n = 0, total = 0;
    document.querySelectorAll('[data-oid]').forEach(function (li) {
      var on = done.has(li.getAttribute('data-oid'));
      li.classList.toggle('done', on);
      var sr = li.querySelector('.sr-state');
      if (sr) sr.textContent = on ? 'done' : 'not done';
    });
    (p.objectives || []).forEach(function (o) { total++; if (done.has(o.id)) n++; });
    if (!total) total = document.querySelectorAll('#labObjectives [data-oid]').length;
    if (!n) n = done.size;
    var pct = Math.round(p.score || 0);
    var bar = document.getElementById('labScoreBar');
    if (bar) { bar.style.width = pct + '%'; bar.parentNode.setAttribute('aria-valuenow', pct); }
    var pbq = !!document.querySelector('[data-pbq]');
    document.querySelectorAll('.lab-score-text').forEach(function (s) { s.textContent = n + ' of ' + total + (pbq ? ' checks · ' : ' objectives · ') + pct + '%'; });
    if (pbq) (p.objectives || []).forEach(function (o) {   // PBQ: the server sends the real texts once the ticket is resolved
      var t = document.querySelector('[data-oid="' + o.id + '"] .obj-text');
      if (t && o.text) t.textContent = o.text;
    });
    var succ = document.getElementById('labSuccess');
    if (succ) succ.hidden = !p.complete;
    document.querySelectorAll('.lab-complete-flag').forEach(function (f) { f.hidden = !p.complete; });
    if (!first && p.newly && p.newly.length) {
      var texts = (p.objectives || []).filter(function (o) { return p.newly.indexOf(o.id) >= 0; }).map(function (o) { return o.text; });
      // r5: one check can complete many objectives at once; a toast listing them all covered the phone screen
      this.toast(texts.length > 2 ? '✓ ' + texts.length + ' objectives complete (' + n + ' of ' + total + ')' : '✓ ' + texts.join(' · '), 'ok');
      this.say('Objective complete: ' + texts.join('; ') + '. ' + n + ' of ' + total + ' done.');
      if (p.complete) this.say('Lab complete. ' + (p.success_msg || ''));
    }
    var self = this;
    this.handlers.forEach(function (fn) { fn(p, first, self); });
  };

  Kit.prototype.hint = function () {
    var self = this;
    this.post(this.urls.hint).then(function (p) {
      self.apply(p);
      var h = p.hint || {};
      var box = document.getElementById('hintBox');
      if (box) {
        box.hidden = false;
        box.innerHTML = '';
        box.appendChild(el('div', { class: 'fw-semibold', text: h.objective_text ? ('Hint ' + h.tier + ' of 2 — ' + h.objective_text) : 'Hint' }));
        box.appendChild(el('div', { class: 'lab-hint-text', text: h.text || '' }));
        if (h.max) box.appendChild(el('div', { class: 'small text-muted mt-1', text: 'That is the full answer for this objective.' }));
        self.say('Hint: ' + (h.text || ''));
      }
      // phones: the side panel is behind the full-screen terminal, so the hint is shown in the terminal too
      self.note(h.objective_text ? ('Hint ' + h.tier + ' of 2 — ' + h.objective_text) : 'Hint', [h.text || ''], 'hint', h.max ? 'That is the full answer for this objective.' : '');
    });
  };

  /* r5: a note inside the terminal (#termNote): hints and check results while the phone terminal is full-screen.
   * Shown only when the terminal is in focus mode (or force); otherwise the side panel / feedback area has it. */
  Kit.prototype.note = function (title, items, kind, foot, force) {
    var box = document.getElementById('termNote');
    if (!box) return false;
    if (!force && !document.documentElement.classList.contains('term-focus-on')) { box.hidden = true; return false; }
    var body = box.querySelector('.term-note-body');
    body.innerHTML = '';
    body.appendChild(el('div', { class: 'term-note-title', text: title }));
    items = (items || []).filter(function (t) { return t; });
    if (items.length === 1) body.appendChild(el('div', { class: kind === 'hint' ? 'lab-hint-text' : '', text: items[0] }));
    else if (items.length) body.appendChild(el('ul', null, items.map(function (t) { return el('li', { text: t }); })));
    if (foot) body.appendChild(el('div', { class: 'small mt-1', text: foot }));
    box.className = 'term-note ' + (kind || '');
    box.hidden = false;
    box.scrollTop = 0;
    if (!box._wired) {
      box._wired = true;
      var x = document.getElementById('termNoteX');
      if (x) {
        x.addEventListener('pointerdown', function (e) { e.preventDefault(); });   // keep the on-screen keyboard open
        x.addEventListener('click', function () { box.hidden = true; var i = document.getElementById('termInput'); if (i && document.documentElement.classList.contains('term-focus-on')) i.focus({ preventScroll: true }); });
      }
    }
    return true;
  };

  Kit.prototype.undo = function () {
    var self = this;
    this.post(this.urls.undo).then(function (p) {
      self.apply(p);
      self.toast(p.undone ? 'Last change undone.' : 'Nothing to undo.', p.undone ? 'ok' : '');
      if (self.onUndo) self.onUndo(p);
    });
  };

  Kit.prototype.reset = function () {
    if (!window.confirm('Start this lab again from the beginning? Your best score is kept.')) return;
    this.post(this.urls.reset).then(function () { window.location.reload(); });
  };

  /* ------------------------------------------------------------------ graded steps */

  function Steps(kit, root) {
    this.kit = kit;
    this.root = root;
    this.drafts = {};
    var self = this;
    kit.on(function (p) { if (p.steps) self.render(p.steps); });
    this.render(kit.state.steps || []);
  }

  Steps.prototype.render = function (steps) {
    var self = this;
    var focusId = document.activeElement && document.activeElement.id;
    steps.forEach(function (s, i) {
      var card = self.root.querySelector('[data-step="' + s.id + '"]');
      var fresh = el('section', { class: 'lab-step card', 'data-step': s.id, 'data-type': s.type, 'aria-labelledby': 'st-' + s.id + '-h' });
      self.build(fresh, s, i);
      if (card) card.replaceWith(fresh); else self.root.appendChild(fresh);
    });
    if (focusId) { var f = document.getElementById(focusId); if (f) f.focus({ preventScroll: true }); }
  };

  Steps.prototype.answerOf = function (s) {
    if (this.drafts[s.id] !== undefined) return this.drafts[s.id];
    return s.saved;
  };

  Steps.prototype.build = function (card, s, i) {
    var self = this;
    var ok = s.last && s.last.correct;
    card.classList.toggle('is-correct', !!ok);
    var head = el('div', { class: 'card-header lab-step-head' }, [
      el('h2', { class: 'h6 mb-0', id: 'st-' + s.id + '-h', text: (s.title ? s.title : 'Step ' + (i + 1)) }),
      ok ? el('span', { class: 'badge text-bg-success', text: '✓ Correct' }) : null
    ]);
    var body = el('div', { class: 'card-body' });
    if (s.prompt) body.appendChild(el('p', { class: 'lab-step-prompt', text: s.prompt }));
    if (s.help) body.appendChild(el('p', { class: 'small text-muted', text: s.help }));
    var widget = el('div', { class: 'lab-step-widget' });
    body.appendChild(widget);
    var fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite', id: 'fb-' + s.id });
    if (s.last && s.last.message) { fb.textContent = s.last.message; fb.classList.add(ok ? 'ok' : 'bad'); }
    var btn = el('button', { type: 'button', class: 'btn btn-brand lab-check', id: 'chk-' + s.id, text: s.submit_label || 'Check answer' });
    btn.addEventListener('click', function () { self.submit(s, card, btn); });
    var row = el('div', { class: 'lab-step-actions' }, [btn]);
    var renderer = this['w_' + s.type];
    var getter = renderer ? renderer.call(this, widget, s) : function () { return null; };
    card._get = getter;
    body.appendChild(row);
    body.appendChild(fb);
    card.appendChild(head);
    card.appendChild(body);
    this.paintPer(card, s.last && s.last.per);
  };

  Steps.prototype.paintPer = function (card, per) {
    if (!per) return;
    Object.keys(per).forEach(function (k) {
      card.querySelectorAll('[data-key="' + CSS.escape(k) + '"]').forEach(function (n) {
        n.classList.toggle('mark-ok', !!per[k]);
        n.classList.toggle('mark-bad', !per[k]);
        var m = n.querySelector('.mark');
        if (m) m.textContent = per[k] ? '✓' : '✗';
      });
    });
  };

  Steps.prototype.submit = function (s, card, btn) {
    var self = this;
    var ans = card._get();
    this.drafts[s.id] = ans;
    btn.disabled = true;
    this.kit.post(this.kit.urls.check, { step: s.id, answer: ans }).then(function (p) {
      btn.disabled = false;
      var r = p.result || {};
      delete self.drafts[s.id];
      self.kit.apply(p);
      var fb = document.getElementById('fb-' + s.id);
      if (fb) { fb.textContent = r.message || ''; fb.className = 'lab-feedback ' + (r.correct ? 'ok' : 'bad'); }
      var nb = document.getElementById('chk-' + s.id);
      if (nb && !r.correct) nb.focus({ preventScroll: true });
      if (r.correct) {
        var nxt = card.nextElementSibling;
        if (nxt && !nxt.classList.contains('is-correct')) {
          var h = nxt.querySelector('h2');
          if (h) { h.setAttribute('tabindex', '-1'); setTimeout(function () { h.focus(); nxt.scrollIntoView({ block: 'start', behavior: 'smooth' }); }, 400); }
        }
      }
    }).catch(function () { btn.disabled = false; });
  };

  /* choice ----------------------------------------------------------- */
  Steps.prototype.w_choice = function (w, s) {
    var saved = this.answerOf(s);
    var name = 'ch-' + s.id;
    var fs = el('fieldset', { class: 'lab-choices' }, [el('legend', { class: 'visually-hidden', text: s.prompt || 'Choose' })]);
    s.options.forEach(function (o, i) {
      var id = name + '-' + i;
      var checked = s.multi ? (Array.isArray(saved) && saved.map(String).indexOf(String(i)) >= 0) : (saved !== undefined && saved !== null && String(saved) === String(i));
      var inp = el('input', { type: s.multi ? 'checkbox' : 'radio', name: name, id: id, value: i, class: 'form-check-input', checked: checked });
      fs.appendChild(el('label', { class: 'lab-choice', for: id, 'data-key': String(i) }, [inp, el('span', { text: o }), el('span', { class: 'mark', 'aria-hidden': 'true' })]));
    });
    if (s.multi) fs.appendChild(el('p', { class: 'small text-muted mb-0', text: 'Choose all that apply.' }));
    w.appendChild(fs);
    return function () {
      var vals = [].slice.call(fs.querySelectorAll('input:checked')).map(function (x) { return parseInt(x.value, 10); });
      return s.multi ? vals : (vals.length ? vals[0] : null);
    };
  };

  /* order (drag with pointer events: mouse + touch; plus move buttons) */
  Steps.prototype.w_order = function (w, s) {
    var saved = this.answerOf(s);
    var items = Array.isArray(saved) && saved.length === s.items.length ? saved.slice() : s.items.slice();
    var list = el('ol', { class: 'lab-order', 'aria-label': 'Items in order. Use the move buttons or drag the handle.' });
    var self = this;
    function draw(focusIdx, focusDir) {
      list.innerHTML = '';
      items.forEach(function (t, i) {
        var up = el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy lab-mv', 'aria-label': 'Move up: ' + t, disabled: i === 0, text: '↑' });
        var dn = el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy lab-mv', 'aria-label': 'Move down: ' + t, disabled: i === items.length - 1, text: '↓' });
        up.addEventListener('click', function () { swap(i, i - 1); draw(i - 1, 'up'); });
        dn.addEventListener('click', function () { swap(i, i + 1); draw(i + 1, 'down'); });
        var handle = el('span', { class: 'lab-handle', 'aria-hidden': 'true', text: '⋮⋮' });
        var li = el('li', { class: 'lab-order-item', 'data-key': t, 'data-i': i }, [handle, el('span', { class: 'lab-order-text', text: t }), el('span', { class: 'mark', 'aria-hidden': 'true' }), up, dn]);
        handle.addEventListener('pointerdown', function (e) { startDrag(e, li, i); });
        list.appendChild(li);
      });
      self.drafts[s.id] = items.slice();
      if (focusIdx !== undefined) {
        var li2 = list.children[focusIdx];
        var b = li2 && li2.querySelector(focusDir === 'up' ? '.lab-mv' : '.lab-mv:last-child');
        if (b && b.disabled) b = li2.querySelector('.lab-mv:not([disabled])');
        if (b) b.focus();
        self.kit.say('Moved to position ' + (focusIdx + 1) + ' of ' + items.length);
      }
    }
    function swap(a, b) { var t = items[a]; items[a] = items[b]; items[b] = t; }
    function startDrag(e, li, idx) {
      e.preventDefault();
      li.setPointerCapture && li.setPointerCapture(e.pointerId);
      li.classList.add('dragging');
      var from = idx;
      function move(ev) {
        var y = ev.clientY;
        var kids = [].slice.call(list.children);
        var to = kids.length - 1;
        for (var k = 0; k < kids.length; k++) {
          var r = kids[k].getBoundingClientRect();
          if (y < r.top + r.height / 2) { to = k; break; }
        }
        if (to !== from) {
          var t = items.splice(from, 1)[0];
          items.splice(to, 0, t);
          from = to;
          draw();
          var n = list.children[from];
          if (n) n.classList.add('dragging');
        }
      }
      function up() {
        document.removeEventListener('pointermove', move);
        document.removeEventListener('pointerup', up);
        document.removeEventListener('pointercancel', up);
        draw();
      }
      document.addEventListener('pointermove', move);
      document.addEventListener('pointerup', up);
      document.addEventListener('pointercancel', up);
    }
    draw();
    w.appendChild(list);
    return function () { return items.slice(); };
  };

  /* match (tap item then tap target; drag also works; keyboard = buttons) */
  Steps.prototype.w_match = function (w, s) {
    var saved = this.answerOf(s) || {};
    var place = Object.assign({}, saved);
    var picked = null;
    var self = this;
    var pool = el('div', { class: 'lab-pool', role: 'group', 'aria-label': 'Items to place' });
    var zones = el('div', { class: 'lab-targets' });
    var hint = el('p', { class: 'small text-muted lab-match-hint', text: 'Tap (or press) an item, then tap the box it belongs in. Drag also works.' });
    function chip(it) {
      var b = el('button', { type: 'button', class: 'lab-chip', 'data-item': it.id, 'data-key': it.id, 'aria-pressed': picked === it.id ? 'true' : 'false' });
      if (it.svg) b.appendChild(el('span', { class: 'lab-chip-svg', html: it.svg }));
      b.appendChild(el('span', { class: 'lab-chip-text', text: it.label }));
      b.appendChild(el('span', { class: 'mark', 'aria-hidden': 'true' }));
      b.addEventListener('click', function () { picked = picked === it.id ? null : it.id; draw(); var n = w.querySelector('[data-item="' + it.id + '"]'); if (n) n.focus(); if (picked) self.kit.say('Selected ' + it.label + '. Now choose a box.'); });
      b.addEventListener('pointerdown', function (e) { if (e.pointerType === 'mouse' && e.button !== 0) return; dragStart(e, it, b); });
      return b;
    }
    function drop(target) {
      if (!picked) return;
      if (target) place[picked] = target; else delete place[picked];
      var lbl = (s.items.filter(function (x) { return x.id === picked; })[0] || {}).label;
      var tl = target ? (s.targets.filter(function (x) { return x.id === target; })[0] || {}).label : 'the pool';
      self.kit.say('Placed ' + lbl + ' in ' + tl + '.');
      picked = null;
      draw();
    }
    function draw() {
      pool.innerHTML = '';
      zones.innerHTML = '';
      s.items.forEach(function (it) { if (!place[it.id]) pool.appendChild(chip(it)); });
      if (!pool.children.length) pool.appendChild(el('span', { class: 'small text-muted', text: 'All items placed. Tap an item to move it back or elsewhere.' }));
      pool.classList.toggle('armed', !!picked && !!place[picked]);
      s.targets.forEach(function (tg) {
        var z = el('div', { class: 'lab-zone' + (picked ? ' armed' : ''), 'data-zone': tg.id });
        var zb = el('button', { type: 'button', class: 'lab-zone-btn', 'aria-label': 'Place here: ' + tg.label, disabled: !picked }, [el('span', { class: 'lab-zone-label', text: tg.label })]);
        zb.addEventListener('click', function () { drop(tg.id); });
        z.appendChild(zb);
        var inner = el('div', { class: 'lab-zone-items' });
        s.items.forEach(function (it) { if (place[it.id] === tg.id) inner.appendChild(chip(it)); });
        z.appendChild(inner);
        zones.appendChild(z);
      });
      self.drafts[s.id] = Object.assign({}, place);
      self.paintPer(w.closest('.lab-step') || w, (s.last && s.last.per) || null);
    }
    pool.addEventListener('click', function (e) { if (e.target === pool && picked && place[picked]) drop(null); });
    function dragStart(e, it, node) {
      var sx = e.clientX, sy = e.clientY, ghost = null, moved = false;
      function mv(ev) {
        if (!moved && Math.abs(ev.clientX - sx) + Math.abs(ev.clientY - sy) < 8) return;
        if (!moved) {
          moved = true; picked = it.id;
          ghost = node.cloneNode(true); ghost.classList.add('lab-ghost'); document.body.appendChild(ghost);
          w.querySelectorAll('.lab-zone').forEach(function (z) { z.classList.add('armed'); });
        }
        ev.preventDefault();
        ghost.style.left = (ev.clientX - 30) + 'px'; ghost.style.top = (ev.clientY - 20) + 'px';
      }
      function up(ev) {
        document.removeEventListener('pointermove', mv);
        document.removeEventListener('pointerup', up);
        document.removeEventListener('pointercancel', up);
        if (!moved) return;
        if (ghost) ghost.remove();
        var under = document.elementFromPoint(ev.clientX, ev.clientY);
        var z = under && under.closest('.lab-zone');
        if (z) drop(z.getAttribute('data-zone'));
        else if (under && under.closest('.lab-pool')) drop(null);
        else { picked = null; draw(); }
        node._suppress = true;
      }
      document.addEventListener('pointermove', mv, { passive: false });
      document.addEventListener('pointerup', up);
      document.addEventListener('pointercancel', up);
    }
    draw();
    w.appendChild(hint);
    w.appendChild(pool);
    w.appendChild(zones);
    return function () { return Object.assign({}, place); };
  };

  /* fields ----------------------------------------------------------- */
  Steps.prototype.w_fields = function (w, s) {
    var saved = this.answerOf(s) || {};
    var grid = el('div', { class: 'lab-fields' });
    var self = this;
    s.fields.forEach(function (f) {
      var id = 'f-' + s.id + '-' + f.name;
      var inp = f.multiline ? el('textarea', { id: id, class: 'form-control', rows: 4, name: f.name, placeholder: f.placeholder || '' })
        : el('input', { id: id, class: 'form-control', type: 'text', name: f.name, placeholder: f.placeholder || '', inputmode: f.inputmode || null,
          autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false' });
      inp.value = saved[f.name] || '';
      inp.addEventListener('input', function () { var a = Object.assign({}, self.drafts[s.id] || saved); a[f.name] = inp.value; self.drafts[s.id] = a; });
      inp.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !f.multiline) { e.preventDefault(); var b = document.getElementById('chk-' + s.id); if (b) b.click(); } });
      grid.appendChild(el('div', { class: 'lab-field' + (f.multiline ? ' wide' : ''), 'data-key': f.name }, [
        el('label', { class: 'form-label', for: id }, [f.label, el('span', { class: 'mark ms-1', 'aria-hidden': 'true' })]), inp]));
    });
    w.appendChild(grid);
    return function () {
      var a = {};
      s.fields.forEach(function (f) { a[f.name] = document.getElementById('f-' + s.id + '-' + f.name).value; });
      return a;
    };
  };

  /* config (settings page) ------------------------------------------- */
  Steps.prototype.w_config = function (w, s) {
    var saved = this.answerOf(s) || {};
    var form = el('div', { class: 'lab-config' });
    s.fields.forEach(function (f) {
      var id = 'c-' + s.id + '-' + f.name;
      var val = saved[f.name] !== undefined ? saved[f.name] : f.default;
      var ctl;
      if (f.kind === 'select') {
        ctl = el('select', { id: id, class: 'form-select', name: f.name });
        (f.options || []).forEach(function (o) { var op = el('option', { value: o[0], text: o[1] }); if (String(o[0]) === String(val)) op.selected = true; ctl.appendChild(op); });
      } else if (f.kind === 'toggle') {
        ctl = el('input', { id: id, type: 'checkbox', role: 'switch', class: 'form-check-input lab-switch', name: f.name, checked: String(val) === 'on' });
      } else {
        ctl = el('input', { id: id, type: f.kind === 'password' ? 'text' : 'text', class: 'form-control' + (f.kind === 'password' ? ' lab-secret' : ''), name: f.name,
          autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false' });
        ctl.value = val || '';
      }
      var row = el('div', { class: 'lab-config-row' + (f.kind === 'toggle' ? ' toggle' : ''), 'data-key': f.name }, [
        el('label', { for: id, class: 'form-label' }, [f.label, el('span', { class: 'mark ms-1', 'aria-hidden': 'true' })]), ctl,
        f.help ? el('div', { class: 'form-text', text: f.help }) : null]);
      form.appendChild(row);
    });
    w.appendChild(form);
    return function () {
      var a = {};
      s.fields.forEach(function (f) {
        var n = document.getElementById('c-' + s.id + '-' + f.name);
        a[f.name] = f.kind === 'toggle' ? (n.checked ? 'on' : 'off') : n.value;
      });
      return a;
    };
  };

  /* build (one part per slot, running total) ------------------------- */
  Steps.prototype.w_build = function (w, s) {
    var saved = this.answerOf(s) || {};
    var grid = el('div', { class: 'lab-build' });
    var total = el('div', { class: 'lab-build-total', role: 'status', 'aria-live': 'polite' });
    function sum() {
      var t = 0;
      s.slots.forEach(function (sl) {
        var v = document.getElementById('b-' + s.id + '-' + sl.name).value;
        var o = sl.options.filter(function (x) { return x.id === v; })[0];
        if (o) t += o.price || 0;
        var spec = document.getElementById('bs-' + s.id + '-' + sl.name);
        if (spec) spec.textContent = o ? o.specs : '';
      });
      total.textContent = 'Total $' + t + (s.budget ? ' of $' + s.budget + ' budget' : '');
      total.classList.toggle('over', !!(s.budget && t > s.budget));
    }
    s.slots.forEach(function (sl) {
      var id = 'b-' + s.id + '-' + sl.name;
      var sel = el('select', { id: id, class: 'form-select', name: sl.name, 'aria-describedby': 'bs-' + s.id + '-' + sl.name });
      sel.appendChild(el('option', { value: '', text: '— choose —' }));
      sl.options.forEach(function (o) { var op = el('option', { value: o.id, text: o.label + '  ($' + o.price + ')' }); if (saved[sl.name] === o.id) op.selected = true; sel.appendChild(op); });
      sel.addEventListener('change', sum);
      grid.appendChild(el('div', { class: 'lab-build-slot', 'data-key': sl.name }, [
        el('label', { class: 'form-label', for: id }, [sl.label, el('span', { class: 'mark ms-1', 'aria-hidden': 'true' })]), sel,
        el('div', { class: 'form-text', id: 'bs-' + s.id + '-' + sl.name })]));
    });
    w.appendChild(grid);
    w.appendChild(total);
    setTimeout(sum, 0);
    return function () {
      var a = {};
      s.slots.forEach(function (sl) { a[sl.name] = document.getElementById('b-' + s.id + '-' + sl.name).value; });
      return a;
    };
  };

  window.LabKit = {
    el: el,
    init: function (cfg) {
      var kit = new Kit(cfg);
      var root = document.getElementById('labSteps');
      if (root && (cfg.boot.steps || []).length) kit.steps = new Steps(kit, root);
      return kit;
    },
    config: function () {
      var n = document.getElementById('labConfig');
      return n ? JSON.parse(n.textContent) : null;
    }
  };
})();
