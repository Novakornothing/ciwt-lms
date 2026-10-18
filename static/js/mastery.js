/* Mastery (pass 11): fills the override dialog from the cell or button that opened it. */
(function () {
  var modal = document.getElementById('mxOverride');
  if (!modal) return;
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
    set('state', b.getAttribute('data-mx-state') || (sr ? sr.textContent : '').replace(/\. Open override$/, ''));
    var t = b.getAttribute('data-mx-target');
    var sel = modal.querySelector('[data-mx="target"]');
    if (sel && t && sel.querySelector('option[value="' + t + '"]')) sel.value = t;
  });
})();
