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
  var HELIX_VISITS = 3, HELIX_DWELL_MS = 120000;
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
    function put() {
      box.replaceWith(fresh);
      document.dispatchEvent(new CustomEvent('ladder:updated'));
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

  function submitForm(box, form, extra) {
    var data = new FormData(form);
    Object.keys(extra || {}).forEach(function (k) { data.set(k, extra[k]); });
    var btn = form.querySelector('[type="submit"]');
    if (btn) btn.disabled = true;
    return post(form.action, data).then(function (j) {
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

  function helixWatch() {
    var H = window.HelixRuntime;
    if (!H || !H.state || !H.state.sessionId || !H.state.timeline) return;
    var buckets = H.state.timeline.buckets || {};
    var byLabel = {};
    Object.keys(buckets).forEach(function (k) {
      var b = buckets[k];
      if ((b.aoi_kind || 'heading') !== 'heading') return;
      var a = byLabel[b.aoi_label] || (byLabel[b.aoi_label] = { visits: 0, dwell: 0 });
      a.visits += b.visits || 0; a.dwell += b.dwell_ms || 0;
    });
    body.querySelectorAll('.ladder[data-next="1"]').forEach(function (box) {
      var sid = box.getAttribute('data-ladder-sid');
      if (offered[sid]) return;
      var a = byLabel[box.getAttribute('data-heading')];
      if (!a || (a.visits < HELIX_VISITS && a.dwell < HELIX_DWELL_MS)) return;
      offered[sid] = true;
      var fd = new FormData(); fd.set('kind', 'helix_offer');
      post(box.getAttribute('data-event-url'), fd).then(function (j) {
        if (!j.ok) return;
        var slot = box.querySelector('.ladder-helix');
        var another = box.querySelector('form.ladder-another');
        if (!slot || !another) return;
        slot.innerHTML = '<p class="small mb-2"><i class="bi bi-eye" aria-hidden="true"></i> Helix (you turned it on) noticed you ' +
          (a.visits >= HELIX_VISITS ? 'came back to this section ' + a.visits + ' times' : 'spent a while on this section') +
          '. Would another explanation help? It is only an offer.</p>' +
          '<button type="button" class="btn btn-sm btn-brand me-2" data-hx-yes>Yes, explain it another way</button>' +
          '<button type="button" class="btn btn-sm btn-outline-navy" data-hx-no>No thanks</button>';
        slot.hidden = false;
        slot.querySelector('[data-hx-yes]').addEventListener('click', function () { submitForm(box, another, { source: 'helix' }); });
        slot.querySelector('[data-hx-no]').addEventListener('click', function () { slot.hidden = true; slot.innerHTML = ''; });
      }).catch(function () {});
    });
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
      f.addEventListener('submit', function (e) { e.preventDefault(); submitForm(box, f); });
    });
    var tog = box.querySelector('.ladder-orig-toggle');
    if (tog) {
      tog.addEventListener('click', function (e) { if (toggleOriginal(box, tog)) e.preventDefault(); });
      tog.addEventListener('keydown', function (e) { if (e.key === ' ') { e.preventDefault(); toggleOriginal(box, tog); } });
    }
    initWidgets(box);
  }

  body.querySelectorAll('.ladder').forEach(init);
  setInterval(helixWatch, 5000);
  window.CiwtLadder = { swap: swap, init: init };
})();
