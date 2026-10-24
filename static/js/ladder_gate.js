/* Comprehension gate + flow: refresh the "X of Y sections verified" banner, lift section locks, and point each
   "Continue" chip at the next section (or the next lesson once all are verified). The server re-checks on
   "Next lesson" (lesson_advance), so this script is a convenience, not the enforcement. */
(function () {
  'use strict';
  var box = document.getElementById('ladderGate');
  var url = box && box.getAttribute('data-gate-url');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var allDone = box ? box.classList.contains('is-done') : false;

  function anchors() { return Array.prototype.slice.call(document.querySelectorAll('.ladder-anchor')); }
  function nextLessonLink() { return document.querySelector('a[data-gated]'); }

  function wireChips() {
    var list = anchors();
    document.querySelectorAll('[data-continue]').forEach(function (chip) {
      var i = list.findIndex(function (a) { return a.id === 'ladder-sec-' + chip.getAttribute('data-continue'); });
      var nxt = i >= 0 ? list[i + 1] : null;
      var lesson = nextLessonLink();
      if (nxt && !allDone) {
        chip.href = '#' + nxt.id;
        chip.textContent = 'Next section ↓';
      } else if (allDone && lesson) {
        chip.href = lesson.getAttribute('href');
        var t = lesson.textContent.trim().replace(/\s+/g, ' ').replace(/^Next lesson/, 'Continue to next lesson');
        chip.textContent = 'All sections verified — ' + t + (/→$/.test(t) ? '' : ' →');
      } else if (nxt) {
        chip.href = '#' + nxt.id;
      }
    });
  }

  document.addEventListener('click', function (e) {
    var chip = e.target.closest && e.target.closest('[data-continue]');
    if (!chip || chip.getAttribute('href').charAt(0) !== '#') return;
    var t = document.getElementById(chip.getAttribute('href').slice(1));
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    var sec = t.nextElementSibling;
    while (sec && !sec.classList.contains('ladder')) sec = sec.nextElementSibling;
    var focusTo = sec && (sec.querySelector('h2, h3, .ladder-label') || sec);
    if (focusTo) { if (!focusTo.hasAttribute('tabindex')) focusTo.setAttribute('tabindex', '-1'); focusTo.focus({ preventScroll: true }); }
    history.replaceState(null, '', '#' + t.id);
  });

  function render(g) {
    allDone = !g.blocked;
    box.querySelector('[data-gate-count]').textContent = g.done + ' of ' + g.total;
    var top = document.querySelector('[data-gate-top-count]');
    if (top) top.textContent = g.done + ' of ' + g.total;
    var bar = box.querySelector('[role="progressbar"]');
    bar.setAttribute('aria-valuenow', g.done);
    bar.firstElementChild.className = 'pf-w-' + Math.floor((100 * g.done / (g.total || 1)) / 5) * 5;
    var list = box.querySelector('[data-gate-list]');
    while (list.firstChild) list.removeChild(list.firstChild);
    g.pending.forEach(function (p) {
      var li = document.createElement('li'), a = document.createElement('a');
      a.href = '#ladder-sec-' + p.sid; a.textContent = p.heading; li.appendChild(a); list.appendChild(li);
    });
    box.querySelector('[data-gate-msg]').textContent = g.blocked
      ? 'What to do next: answer the quick check (not graded) in each section below. If one does not click, press “Explain it another way”. Still to do:'
      : 'All sections verified. Use the button below to move on.';
    box.classList.toggle('is-done', !g.blocked);
    var sids = anchors().map(function (a) { return a.id.replace('ladder-sec-', ''); });
    var firstIdx = g.first ? sids.indexOf(g.first) : -1;
    document.querySelectorAll('.ladder-lock').forEach(function (l) {
      var i = sids.indexOf(l.getAttribute('data-lock-sid'));
      if (firstIdx < 0 || i <= firstIdx) {
        var sec = l.nextElementSibling;
        if (sec && !reduce) { sec.classList.add('ladder-unlocked'); setTimeout(function () { sec.classList.remove('ladder-unlocked'); }, 700); }
        l.remove();
      }
    });
    wireChips();
  }

  document.addEventListener('ladder:updated', function (ev) {
    wireChips();
    var sid = ev.detail && ev.detail.sid;
    var chip = sid && document.querySelector('[data-continue="' + sid + '"]');
    if (!url) { if (chip) chip.focus({ preventScroll: true }); return; }
    fetch(url, { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (g) { if (g) render(g); if (chip) chip.focus({ preventScroll: true }); })
      .catch(function () {});
  });
  wireChips();
})();
