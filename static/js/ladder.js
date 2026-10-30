/* Explanation ladder (pass 19): micro-checks after lesson sections and in-place swaps to another explanation.
   Works without JavaScript (forms post and the page reloads at the section); with it, the section is replaced in
   place, animated (unless reduced motion is on), labelled, and focus moves to the new label.
   Helix (only when the student has consented and a Helix session is running on this page) can OFFER the next
   explanation when a section is re-read several times or read for a long time. It never swaps on its own. */
(function () {
  'use strict';
  var body = document.getElementById('lessonBody');
  if (!body) return;
  var tok = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var HELIX_VISITS = 3, HELIX_DWELL_MS = 22000;
  var offered = {};

  function post(url, data) {
    return fetch(url, { method: 'POST', credentials: 'same-origin', body: data,
      headers: { 'X-Requested-With': 'fetch', 'Accept': 'application/json', 'X-CSRFToken': tok } })
      .then(function (r) { return r.json().then(function (j) { j._status = r.status; return j; }); });
  }

  function swap(box, html, moveFocus) {
    var tmp = document.createElement('div');
    tmp.innerHTML = html.trim();
    var fresh = tmp.firstElementChild;
    // A bulk swap from the 5 Ways to Learn switcher: keep the reader where they are (no focus jump, no scroll).
    if (box.hasAttribute('data-swap-quiet')) moveFocus = false;
    function put() {
      box.replaceWith(fresh);
      document.dispatchEvent(new CustomEvent('ladder:updated', { detail: { sid: fresh.getAttribute('data-ladder-sid') } }));
      if (!reduce) { fresh.classList.add('ladder-entering'); setTimeout(function () { fresh.classList.remove('ladder-entering'); }, 400); }
      init(fresh);
      if (moveFocus) {
        var target = fresh.querySelector('.ladder-label') || fresh.querySelector('.ladder-feedback');
        if (target) {
          if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
          target.focus({ preventScroll: true });
        }
        var top = fresh.getBoundingClientRect().top;
        if (top < 0 || top > window.innerHeight * 0.6) fresh.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      }
    }
    if (reduce) { put(); return; }
    box.classList.add('ladder-leaving');
    setTimeout(put, 190);
  }

  function submitForm(box, form, extra, actionUrl) {
    var data = new FormData(form);
    Object.keys(extra || {}).forEach(function (k) { data.set(k, extra[k]); });
    var btn = form.querySelector('[type="submit"]');
    if (btn) btn.disabled = true;
    return post(actionUrl || form.action, data).then(function (j) {
      if (j.error) {
        var fb = box.querySelector('.ladder-feedback');
        if (fb) { fb.textContent = j.error; fb.className = 'ladder-feedback is-miss'; }
        if (btn) btn.disabled = false;
        return;
      }
      swap(box, j.html, j.shown !== box.getAttribute('data-shown') || true);
    }).catch(function () { form.submit(); });
  }

  function toggleOriginal(box, link) {
    var rung = box.querySelector('.ladder-rung');
    var tpl = box.querySelector('template.ladder-original-tpl');
    if (!rung || !tpl) return false;
    var showingOrig = link.getAttribute('aria-pressed') === 'true';
    var holder = box.querySelector('.ladder-orig-holder');
    if (!showingOrig) {
      if (!holder) {
        holder = document.createElement('div');
        holder.className = 'ladder-orig-holder';
        holder.innerHTML = '<p class="ladder-label"><span class="ladder-badge ladder-badge-orig">Original explanation</span></p>';
        holder.appendChild(tpl.content.cloneNode(true));
        rung.parentNode.insertBefore(holder, rung);
      }
      holder.hidden = false; rung.hidden = true;
      link.setAttribute('data-orig-label', link.textContent);
      link.textContent = link.getAttribute('data-back');
      link.setAttribute('aria-pressed', 'true');
      var fd = new FormData(); fd.set('kind', 'see_original');
      post(box.getAttribute('data-event-url'), fd).catch(function () {});
    } else {
      if (holder) holder.hidden = true;
      rung.hidden = false;
      link.innerHTML = 'See the original explanation<span class="visually-hidden"> of ' + escapeHtml(box.getAttribute('data-heading')) + '</span>';
      link.setAttribute('aria-pressed', 'false');
    }
    return true;
  }

  function escapeHtml(s) { var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

  function initWidgets(box) {
    box.querySelectorAll('.ladder-widget').forEach(function (w) {
      var type = w.getAttribute('data-widget');
      var done = w.querySelector('.ladder-w-done');
      var answer = w.getAttribute('data-answer') ? JSON.parse(w.getAttribute('data-answer')) : null;
      if (type === 'order') {
        var list = w.querySelector('.ladder-order');
        list.addEventListener('click', function (e) {
          var b = e.target.closest('[data-move]');
          if (!b) return;
          var li = b.closest('li'), dir = +b.getAttribute('data-move');
          if (dir < 0 && li.previousElementSibling) list.insertBefore(li, li.previousElementSibling);
          else if (dir > 0 && li.nextElementSibling) list.insertBefore(li.nextElementSibling, li);
          b.focus();
        });
      }
      var check = w.querySelector('[data-wcheck]');
      if (!check) return;
      check.addEventListener('click', function () {
        var ok = false, msg;
        if (type === 'order') {
          var got = Array.prototype.map.call(w.querySelectorAll('.ladder-order li'), function (li) { return li.getAttribute('data-step'); });
          var right = got.filter(function (s, i) { return s === answer[i]; }).length;
          ok = right === answer.length;
          msg = ok ? 'All in order. ' : right + ' of ' + answer.length + ' steps are in the right place. Move the others and check again.';
        } else if (type === 'sort') {
          var sel = w.querySelectorAll('select[data-item]'), n = 0;
          sel.forEach(function (s) { var good = s.value === answer[s.getAttribute('data-item')]; if (good) n++; s.setAttribute('aria-invalid', s.value && !good ? 'true' : 'false'); });
          ok = n === sel.length;
          msg = ok ? 'All sorted correctly. ' : n + ' of ' + sel.length + ' are in the right group. Change the others and check again.';
        }
        if (done) done.textContent = msg + (ok ? done.getAttribute('data-done') : '');
      });
    });
  }

  function nextRungLabel(box) {
    var shown = box.getAttribute('data-shown') || 'R0';
    var map = { R0: 'Plain English', R1: 'Analogy', R2: 'Visual', R3: 'Try-It' };
    var anotherBtn = box.querySelector('form.ladder-another button');
    if (anotherBtn) {
      var m = /\(([^)]+)\)/.exec(anotherBtn.textContent || '');
      if (m && m[1]) {
        return m[1];
      }
    }
    return map[shown] || 'another way';
  }

  function renderHelixNudge(box, stats, force) {
    var sid = box.getAttribute('data-ladder-sid');
    var slot = box.querySelector('.ladder-helix');
    var another = box.querySelector('form.ladder-another');
    if (!slot || !another) return false;
    var visits = (stats && stats.visits) || 3;
    var rLabel = nextRungLabel(box);
    var dock = document.getElementById('helixDock');
    if (dock) {
      dock.setAttribute('data-nudge', sid);
      setTimeout(function () { if (dock.getAttribute('data-nudge') === sid) dock.removeAttribute('data-nudge'); }, 6000);
    }
    slot.innerHTML =
      '<div class="d-flex align-items-start justify-content-between flex-wrap gap-2">' +
        '<p class="small mb-2"><i class="bi bi-eye" aria-hidden="true"></i> <strong>Helix noticed you\u2019re re-reading this section</strong> (' +
          (visits >= HELIX_VISITS ? 'came back to this section ' + visits + ' times' : 'spent a while on this section') +
          ') \u2014 want a clearer explanation? It is only an offer.</p>' +
      '</div>' +
      '<div class="d-flex flex-wrap gap-2 align-items-center">' +
        '<button type="button" class="btn btn-sm btn-brand" data-hx-yes>' +
          '<i class="bi bi-arrow-repeat me-1" aria-hidden="true"></i>Switch to ' + escapeHtml(rLabel) + ' \u2192' +
          '<span class="visually-hidden"> (Yes, explain it another way)</span>' +
        '</button>' +
        '<button type="button" class="btn btn-sm btn-outline-navy" data-hx-no>Dismiss</button>' +
      '</div>';
    slot.hidden = false;
    slot.querySelector('[data-hx-yes]').addEventListener('click', function () {
      document.dispatchEvent(new CustomEvent('helix:ladder-nudge-accepted', {
        detail: { notice: 'ladder_nudge_accepted', secId: sid, rung: rLabel }
      }));
      submitForm(box, another, { source: 'helix' });
    });
    slot.querySelector('[data-hx-no]').addEventListener('click', function () {
      slot.hidden = true;
      slot.innerHTML = '';
    });
    return true;
  }

  function offerForBox(box, stats, skipServerCheck) {
    if (!box) return Promise.resolve(false);
    var sid = box.getAttribute('data-ladder-sid');
    if (!skipServerCheck && offered[sid] && Date.now() - offered[sid] < 90000) return Promise.resolve(false);
    offered[sid] = Date.now();
    if (skipServerCheck) {
      return Promise.resolve(renderHelixNudge(box, stats, true));
    }
    var fd = new FormData();
    fd.set('kind', 'helix_offer');
    return post(box.getAttribute('data-event-url'), fd).then(function (j) {
      if (!j || !j.ok) return false;
      return renderHelixNudge(box, stats, false);
    }).catch(function () { return false; });
  }

  function helixWatch() {
    var H = window.HelixRuntime;
    if (!H || !H.state || !H.state.sessionId || !H.state.timeline) return;
    var buckets = H.state.timeline.buckets || {};
    var byLabel = {}, bySid = {};
    Object.keys(buckets).forEach(function (k) {
      var b = buckets[k];
      if ((b.aoi_kind || 'heading') !== 'heading') return;
      var lbl = (b.aoi_label || '').trim();
      var a = byLabel[lbl] || (byLabel[lbl] = { visits: 0, dwell: 0 });
      a.visits += b.visits || 0;
      a.dwell += b.dwell_ms || 0;
      if (b.ladder_sid) {
        var s = bySid[b.ladder_sid] || (bySid[b.ladder_sid] = { visits: 0, dwell: 0 });
        s.visits += b.visits || 0;
        s.dwell += b.dwell_ms || 0;
      }
    });
    body.querySelectorAll('.ladder[data-next="1"]').forEach(function (box) {
      var sid = box.getAttribute('data-ladder-sid');
      if (offered[sid] && Date.now() - offered[sid] < 90000) return;
      var a = bySid[sid] || byLabel[(box.getAttribute('data-heading') || '').trim()];
      if (!a) return;
      var struggling = (a.visits >= HELIX_VISITS) || (a.dwell >= HELIX_DWELL_MS && a.visits >= 2) || (a.dwell >= 120000);
      if (!struggling) return;
      offerForBox(box, a, false);
    });
  }

  function triggerStruggleNudge(secId, opts) {
    opts = opts || {};
    var box = secId
      ? (document.getElementById('ladder-' + secId) || body.querySelector('.ladder[data-ladder-sid="' + secId + '"]'))
      : body.querySelector('.ladder[data-next="1"]');
    if (!box) return Promise.resolve(false);
    var sid = box.getAttribute('data-ladder-sid');
    delete offered[sid];
    var stats = { visits: opts.visits || 3, dwell: opts.dwellMs || 28000 };
    if (opts.skipServer !== false && (!window.HelixRuntime || !window.HelixRuntime.state || !window.HelixRuntime.state.sessionId)) {
      return offerForBox(box, stats, true);
    }
    return offerForBox(box, stats, !!opts.skipServer);
  }

  function init(box) {
    var check = box.querySelector('form.ladder-check');
    if (check) check.addEventListener('submit', function (e) {
      if (!check.querySelector('input[name="answer"]:checked')) return;   // native "required" message
      e.preventDefault(); submitForm(box, check);
    });
    var another = box.querySelector('form.ladder-another');
    if (another) another.addEventListener('submit', function (e) { e.preventDefault(); submitForm(box, another); });
    box.querySelectorAll('form.ladder-showform').forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var act = (e.submitter && e.submitter.getAttribute('formaction')) || f.action;
        submitForm(box, f, null, act);
      });
    });
    var tog = box.querySelector('.ladder-orig-toggle');
    if (tog) {
      tog.addEventListener('click', function (e) { if (toggleOriginal(box, tog)) e.preventDefault(); });
      tog.addEventListener('keydown', function (e) { if (e.key === ' ') { e.preventDefault(); toggleOriginal(box, tog); } });
    }
    initWidgets(box);
  }

  body.querySelectorAll('.ladder').forEach(init);
  setInterval(helixWatch, 2500);
  window.NovakLadder = window.CiwtLadder = { swap: swap, init: init, helixWatch: helixWatch, triggerStruggleNudge: triggerStruggleNudge };
  window.HelixGaze = window.HelixGaze || {};
  window.HelixGaze.triggerStruggleNudge = triggerStruggleNudge;
})();
