/* Comprehension gate: refresh the "X of Y sections verified" banner and lift section locks after each quick check.
   The server re-checks on "Next lesson" (lesson_advance), so this script is a convenience, not the enforcement. */
(function () {
  'use strict';
  var box = document.getElementById('ladderGate');
  if (!box) return;
  var url = box.getAttribute('data-gate-url');
  function render(g) {
    box.querySelector('[data-gate-count]').textContent = g.done + ' of ' + g.total;
    var bar = box.querySelector('[role="progressbar"]');
    bar.setAttribute('aria-valuenow', g.done);
    var pct = Math.floor((100 * g.done / (g.total || 1)) / 5) * 5;
    bar.firstElementChild.className = 'pf-w-' + pct;
    var list = box.querySelector('[data-gate-list]');
    while (list.firstChild) list.removeChild(list.firstChild);
    g.pending.forEach(function (p) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.href = '#ladder-sec-' + p.sid; a.textContent = p.heading; li.appendChild(a); list.appendChild(li);
    });
    box.querySelector('[data-gate-msg]').textContent = g.blocked
      ? "Answer each section's quick check (not graded) to move on. Still to do:" : 'All sections verified. You can move on.';
    box.classList.toggle('is-done', !g.blocked);
    var firstIdx = -1, sids = [];
    document.querySelectorAll('.ladder-anchor').forEach(function (a) { sids.push(a.id.replace('ladder-sec-', '')); });
    if (g.first) firstIdx = sids.indexOf(g.first);
    document.querySelectorAll('.ladder-lock').forEach(function (l) {
      var i = sids.indexOf(l.getAttribute('data-lock-sid'));
      if (firstIdx < 0 || i <= firstIdx) l.remove();
    });
  }
  document.addEventListener('ladder:updated', function () {
    fetch(url, { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; }).then(function (g) { if (g) render(g); }).catch(function () {});
  });
})();
