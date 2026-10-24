/* Exam-Day Readiness Simulator: countdown (pausable in practice mode, strict in exam mode), flag for review,
   skip PBQs and return later, and the answered / unanswered / flagged review grid. */
(function () {
  'use strict';
  var root = document.getElementById('examSim');
  var form = document.getElementById('esForm');
  if (!root || !form) return;
  var strict = root.dataset.strict === '1';
  var left = parseInt(root.dataset.remaining, 10) || 0;
  var clock = document.getElementById('esClock');
  var paused = false, submitted = false;
  var qs = Array.prototype.slice.call(document.querySelectorAll('.es-q'));

  function fmt(s) {
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
    return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (x < 10 ? '0' : '') + x;
  }
  function tick() {
    if (submitted) return;
    if (!paused) left = Math.max(0, left - 1);
    clock.textContent = fmt(left);
    root.classList.toggle('es-low', left <= 300);
    if (left === 0) {
      submitted = true;
      document.getElementById('esTimedOut').value = '1';
      form.submit();
    }
  }
  clock.textContent = fmt(left);
  setInterval(tick, 1000);

  var pause = document.getElementById('esPause');
  if (pause && !strict) {
    pause.addEventListener('click', function () {
      paused = !paused;
      pause.setAttribute('aria-pressed', paused ? 'true' : 'false');
      pause.textContent = paused ? 'Resume timer' : 'Pause timer';
      document.getElementById('esPausedNote').classList.toggle('d-none', !paused);
      document.getElementById('esQuestions').classList.toggle('es-hidden', paused);
    });
  }

  var skip = document.getElementById('esSkipPbq');
  if (skip) {
    skip.addEventListener('click', function () {
      var list = document.getElementById('esQuestions');
      var pbqs = qs.filter(function (q) { return q.classList.contains('es-pbq'); });
      var skipped = skip.dataset.skipped === '1';
      pbqs.forEach(function (q) { if (skipped) list.insertBefore(q, list.firstChild); else list.appendChild(q); });
      if (skipped) pbqs.reverse().forEach(function (q) { list.insertBefore(q, list.firstChild); });
      skip.dataset.skipped = skipped ? '0' : '1';
      skip.textContent = skipped ? 'Skip PBQs & return later' : 'Back to PBQs';
      var first = skipped ? pbqs[0] : list.querySelector('.es-q:not(.es-pbq)');
      if (first) first.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function answered(q) {
    return Array.prototype.some.call(q.querySelectorAll('input[name^="q"], select'), function (el) {
      return (el.type === 'radio' || el.type === 'checkbox') ? el.checked : !!el.value;
    });
  }
  function refresh() {
    var a = 0, f = 0;
    qs.forEach(function (q) {
      var n = q.dataset.n, cell = document.querySelector('.es-cell[data-n="' + n + '"]');
      var isA = answered(q), isF = q.querySelector('.es-flag-box').checked;
      a += isA ? 1 : 0; f += isF ? 1 : 0;
      cell.classList.toggle('es-answered', isA);
      cell.classList.toggle('es-unanswered', !isA);
      cell.classList.toggle('es-flagged', isF);
      q.classList.toggle('es-is-flagged', isF);
    });
    document.getElementById('esCounts').textContent =
      'Answered ' + a + ' · Unanswered ' + (qs.length - a) + ' · Flagged ' + f;
  }
  form.addEventListener('change', refresh);
  refresh();

  form.addEventListener('submit', function (e) {
    if (submitted) return;
    var un = qs.filter(function (q) { return !answered(q); }).length;
    var fl = form.querySelectorAll('.es-flag-box:checked').length;
    if ((un || fl) && !window.confirm('You have ' + un + ' unanswered and ' + fl + ' flagged question(s). Submit anyway?')) {
      e.preventDefault();
      document.getElementById('esReview').scrollIntoView({ behavior: 'smooth' });
      return;
    }
    submitted = true;
  });
})();
