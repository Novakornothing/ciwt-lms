/* Mastery (pass 11): fills the override dialog from the cell or button that opened it.
   Pass 14: the status line follows the "Applies to" choice (per-student status lines in #mxStates). */
(function () {
  var modal = document.getElementById('mxOverride');
  if (!modal) return;
  var states = {};
  var blob = document.getElementById('mxStates');
  if (blob) { try { states = JSON.parse(blob.textContent) || {}; } catch (e) { states = {}; } }
  var stateEl = modal.querySelector('[data-mx="state"]');
  var sel = modal.querySelector('[data-mx="target"]');
  var userEl = modal.querySelector('[data-mx="user"]');
  var fallback = '';
  var describe = function () {
    if (!stateEl || !sel) return;
    var u = userEl ? userEl.value : '';
    var line = (states[u] || {})[sel.value];
    stateEl.textContent = line || (sel.value === modal.getAttribute('data-mx-opened') ? fallback : '');
  };
  modal.addEventListener('show.bs.modal', function (ev) {
    var b = ev.relatedTarget;
    if (!b) return;
    var set = function (k, v) {
      var el = modal.querySelector('[data-mx="' + k + '"]');
      if (!el || v == null) return;
      if ('value' in el && el.tagName !== 'P' && el.tagName !== 'SPAN') el.value = v; else el.textContent = v;
    };
    set('user', b.getAttribute('data-mx-user'));
    set('name', b.getAttribute('data-mx-name'));
    var sr = b.querySelector('.mx-cell-sr');
    fallback = b.getAttribute('data-mx-state') || (sr ? sr.textContent : '').replace(/\. Open override$/, '');
    set('state', fallback);
    var t = b.getAttribute('data-mx-target');
    if (sel && t && sel.querySelector('option[value="' + t + '"]')) sel.value = t;
    modal.setAttribute('data-mx-opened', sel ? sel.value : '');
    describe();
  });
  if (sel) sel.addEventListener('change', describe);
})();

/* Briefing (pass 12): print button (no inline handlers, CSP-friendly). */
(function () {
  document.querySelectorAll('[data-mx-print]').forEach(function (b) {
    b.addEventListener('click', function () { window.print(); });
  });
})();
