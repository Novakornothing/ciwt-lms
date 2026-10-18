/* Shared quiz/test runner (pass 6). One question at a time, navigator, flag, review-before-submit,
 * optional countdown with auto-submit, answers kept in sessionStorage so a reload or accidental
 * back does not lose work. Options are built with textContent (question banks contain <tags>). */
(function () {
  'use strict';
  var shell = document.querySelector('[data-assessment]');
  if (!shell) return;
  var cfg = shell.dataset;
  var questions = JSON.parse(document.getElementById('assessQuestions').textContent || '[]');
  var storeKey = 'ciwt-assess:' + cfg.storeKey;
  var state = { answers: {}, flagged: [], touched: {} };
  var P = window.CIWTPBQ || null;   // pass 11: choose-N / ordering / matching items (static/js/pbq-core.js)
  try { var saved = JSON.parse(sessionStorage.getItem(storeKey) || 'null'); if (saved && saved.answers) state = saved; } catch (e) {}
  var flagged = new Set(state.flagged || []);
  var answers = state.answers || {};
  var touched = state.touched || {};
  function typed(q) { return !!(P && q && q.type && q.type !== 'single'); }
  function isAns(i) { var q = questions[i]; return typed(q) ? P.isAnswered(q, answers[i], touched[i]) : answers[i] != null; }
  var idx = 0;
  var submitting = false;

  var $ = function (id) { return document.getElementById(id); };
  var qNav = $('qNav'), qText = $('qText'), qOptions = $('qOptions'), qLo = $('qLo');
  var progressLabel = $('progressLabel'), progressBar = $('progressBar');
  var prevBtn = $('prevBtn'), nextBtn = $('nextBtn'), submitBtn = $('submitBtn'), flagBtn = $('flagBtn');
  var form = $('testForm'), live = $('assessLive');

  document.body.classList.add('assess-focus');

  function persist() {
    try { sessionStorage.setItem(storeKey, JSON.stringify({ answers: answers, flagged: Array.from(flagged), touched: touched })); } catch (e) {}
  }
  function answeredCount() { var n = 0; questions.forEach(function (_, i) { if (isAns(i)) n++; }); return n; }

  function buildNav() {
    qNav.textContent = '';
    questions.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = String(i + 1);
      b.addEventListener('click', function () { go(i); });
      qNav.appendChild(b);
    });
  }

  function syncNav() {
    Array.prototype.forEach.call(qNav.children, function (b, i) {
      b.className = '';
      var bits = ['Question ' + (i + 1)];
      if (isAns(i)) { b.classList.add('answered'); bits.push('answered'); } else bits.push('not answered');
      if (flagged.has(i)) { b.classList.add('flagged'); bits.push('flagged'); }
      if (i === idx) {
        b.classList.add('current'); b.setAttribute('aria-current', 'step');
        if (qNav.scrollWidth > qNav.clientWidth) { var l = b.offsetLeft - qNav.offsetLeft; if (l < qNav.scrollLeft || l + b.offsetWidth > qNav.scrollLeft + qNav.clientWidth) qNav.scrollLeft = l - qNav.clientWidth / 2 + b.offsetWidth / 2; }
      } else b.removeAttribute('aria-current');
      b.setAttribute('aria-label', bits.join(', '));
    });
    var n = answeredCount();
    progressLabel.textContent = 'Question ' + (idx + 1) + ' of ' + questions.length + ' · ' + n + ' answered';
    if (progressBar) progressBar.style.width = Math.round(100 * n / Math.max(1, questions.length)) + '%';
    flagBtn.setAttribute('aria-pressed', flagged.has(idx) ? 'true' : 'false');
    flagBtn.querySelector('i').className = flagged.has(idx) ? 'bi bi-flag-fill' : 'bi bi-flag';
    flagBtn.querySelector('.lbl').textContent = flagged.has(idx) ? 'Flagged' : 'Flag';
  }

  function render(focusQuestion) {
    var q = questions[idx];
    qText.textContent = (idx + 1) + '. ' + q.text;
    qLo.textContent = '';
    var ic = document.createElement('i'); ic.className = 'bi bi-bullseye'; ic.setAttribute('aria-hidden', 'true');
    var code = document.createElement('strong'); code.textContent = q.lo || q.lo_code || 'LO';
    qLo.append(ic, ' ', code, ' · ' + (q.lo_text || 'Linked learning objective'));

    qOptions.textContent = '';
    if (typed(q)) { renderTyped(q); }
    else {
    qOptions.setAttribute('role', 'radiogroup');
    (q.options || []).forEach(function (opt, oi) {
      var lab = document.createElement('label');
      lab.className = 'q-option' + (answers[idx] === opt ? ' selected' : '');
      var input = document.createElement('input');
      input.type = 'radio'; input.name = '_choice'; input.value = String(oi);
      input.className = 'q-radio'; input.checked = answers[idx] === opt;
      var key = document.createElement('span'); key.className = 'q-key'; key.setAttribute('aria-hidden', 'true');
      key.textContent = String.fromCharCode(65 + oi);
      var txt = document.createElement('span'); txt.className = 'q-text'; txt.textContent = String(opt);
      input.addEventListener('change', function () {
        answers[idx] = opt; persist();
        Array.prototype.forEach.call(qOptions.children, function (l) { l.classList.toggle('selected', l === lab); });
        syncNav();
      });
      lab.append(input, key, txt);
      qOptions.appendChild(lab);
    });
    }

    prevBtn.disabled = idx === 0;
    var last = idx === questions.length - 1;
    nextBtn.classList.toggle('d-none', last);
    submitBtn.classList.toggle('d-none', !last);
    syncNav();
    if (focusQuestion) {
      qText.focus({ preventScroll: true });
      var top = $('qCard').getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--assess-top'), 10) || 120);
      if (window.scrollY > top) window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
      if (live) live.textContent = 'Question ' + (idx + 1) + ' of ' + questions.length;
    }
  }

  // ---- pass 11: performance-based item types. Every control is a native checkbox, button or select, so it works
  // with a keyboard, a screen reader and touch; changes are announced in the polite live region.
  function say(msg) { if (live) live.textContent = msg; }
  function hint(text) { var h = document.createElement('p'); h.className = 'pbq-hint'; h.id = 'pbqHint'; h.textContent = text; return h; }
  function renderTyped(q) {
    if (answers[idx] == null) answers[idx] = P.initial(q);
    if (q.type === 'multi') {
      qOptions.setAttribute('role', 'group');
      qOptions.appendChild(hint('Choose ' + q.choose + '. ' + answers[idx].length + ' of ' + q.choose + ' chosen.'));
      (q.options || []).forEach(function (opt, oi) {
        var lab = document.createElement('label');
        var on = answers[idx].indexOf(opt) >= 0;
        lab.className = 'q-option pbq-check' + (on ? ' selected' : '');
        var input = document.createElement('input');
        input.type = 'checkbox'; input.className = 'q-radio'; input.checked = on; input.value = String(oi);
        input.setAttribute('aria-describedby', 'pbqHint');
        var key = document.createElement('span'); key.className = 'q-key q-key-sq'; key.setAttribute('aria-hidden', 'true');
        key.textContent = String.fromCharCode(65 + oi);
        var txt = document.createElement('span'); txt.className = 'q-text'; txt.textContent = String(opt);
        input.addEventListener('change', function () {
          var next = P.toggle(answers[idx], opt, q.choose);
          if (input.checked && next.indexOf(opt) < 0) { input.checked = false; say('You can choose only ' + q.choose + '. Clear one first.'); return; }
          answers[idx] = next; persist();
          lab.classList.toggle('selected', input.checked);
          $('pbqHint').textContent = 'Choose ' + q.choose + '. ' + next.length + ' of ' + q.choose + ' chosen.';
          syncNav();
        });
        lab.append(input, key, txt);
        qOptions.appendChild(lab);
      });
    } else if (q.type === 'order') {
      qOptions.removeAttribute('role');
      qOptions.appendChild(hint('Use Move up and Move down to put the steps in order, first step at the top.'));
      var ol = document.createElement('ol'); ol.className = 'pbq-order'; ol.setAttribute('aria-describedby', 'pbqHint');
      answers[idx].forEach(function (step, si) {
        var li = document.createElement('li'); li.className = 'pbq-step';
        var num = document.createElement('span'); num.className = 'q-key'; num.setAttribute('aria-hidden', 'true'); num.textContent = String(si + 1);
        var txt = document.createElement('span'); txt.className = 'q-text'; txt.textContent = String(step);
        var tools = document.createElement('span'); tools.className = 'pbq-tools';
        [[-1, 'up', 'bi-arrow-up'], [1, 'down', 'bi-arrow-down']].forEach(function (d) {
          var b = document.createElement('button'); b.type = 'button'; b.className = 'btn btn-sm btn-outline-navy pbq-move';
          b.dataset.dir = d[1];
          b.setAttribute('aria-label', 'Move “' + step + '” ' + d[1]);
          b.disabled = (d[0] < 0 && si === 0) || (d[0] > 0 && si === answers[idx].length - 1);
          var ic = document.createElement('i'); ic.className = 'bi ' + d[2]; ic.setAttribute('aria-hidden', 'true'); b.appendChild(ic);
          b.addEventListener('click', function () {
            var r = P.move(answers[idx], si, d[0]);
            answers[idx] = r.list; touched[idx] = true; persist();
            render(false);
            var btns = qOptions.querySelectorAll('.pbq-step')[r.index].querySelectorAll('.pbq-move');
            var keep = btns[d[0] < 0 ? 0 : 1]; (keep.disabled ? btns[d[0] < 0 ? 1 : 0] : keep).focus();
            say('“' + step + '” moved to position ' + (r.index + 1) + ' of ' + r.list.length + '.');
          });
          tools.appendChild(b);
        });
        li.append(num, txt, tools); ol.appendChild(li);
      });
      qOptions.appendChild(ol);
      var keepBtn = document.createElement('button'); keepBtn.type = 'button'; keepBtn.className = 'btn btn-sm btn-outline-gold pbq-confirm';
      keepBtn.textContent = touched[idx] ? 'Order saved' : 'Use this order';
      keepBtn.setAttribute('aria-pressed', touched[idx] ? 'true' : 'false');
      keepBtn.addEventListener('click', function () { touched[idx] = true; persist(); keepBtn.textContent = 'Order saved'; keepBtn.setAttribute('aria-pressed', 'true'); syncNav(); say('Order saved.'); });
      qOptions.appendChild(keepBtn);
    } else if (q.type === 'match') {
      qOptions.removeAttribute('role');
      qOptions.appendChild(hint('Choose the best match for each item. Some choices may not be used.'));
      (q.prompts || []).forEach(function (pr, ri) {
        var row = document.createElement('div'); row.className = 'pbq-match';
        var id = 'pbqm-' + idx + '-' + ri;
        var lab = document.createElement('label'); lab.setAttribute('for', id); lab.className = 'pbq-prompt'; lab.textContent = String(pr);
        var sel = document.createElement('select'); sel.id = id; sel.className = 'form-select pbq-select';
        var o0 = document.createElement('option'); o0.value = ''; o0.textContent = 'Choose…'; sel.appendChild(o0);
        (q.options || []).forEach(function (opt) { var o = document.createElement('option'); o.value = String(opt); o.textContent = String(opt); sel.appendChild(o); });
        sel.value = answers[idx][ri] || '';
        sel.addEventListener('change', function () { answers[idx] = P.setMatch(answers[idx], ri, sel.value, q.prompts.length); persist(); syncNav(); });
        row.append(lab, sel); qOptions.appendChild(row);
      });
    }
  }

  function go(i) { if (i < 0 || i >= questions.length) return; idx = i; render(true); }

  function syncHidden() {
    form.querySelectorAll('input[type=hidden][data-ans]').forEach(function (el) { el.remove(); });
    Object.keys(answers).forEach(function (i) {
      if (answers[i] == null) return;
      var q = questions[i];
      if (typed(q) && !isAns(i) && !(Array.isArray(answers[i]) && answers[i].some(function (v) { return v; }))) return;
      var h = document.createElement('input');
      h.type = 'hidden'; h.name = 'q' + i; h.value = typed(q) ? P.serialize(q, answers[i]) : answers[i]; h.dataset.ans = '1';
      form.appendChild(h);
    });
  }

  function doSubmit(timedOut) {
    if (submitting) return;
    submitting = true;
    syncHidden();
    if (timedOut) { var t = $('timedOutField'); if (t) t.value = '1'; }
    try { sessionStorage.removeItem(storeKey); } catch (e) {}
    var c = $('confirmSubmit');
    if (c) { c.disabled = true; c.classList.add('is-busy'); }
    submitBtn.disabled = true;
    form.submit();
  }

  prevBtn.addEventListener('click', function () { go(idx - 1); });
  nextBtn.addEventListener('click', function () { go(idx + 1); });
  flagBtn.addEventListener('click', function () {
    if (flagged.has(idx)) flagged.delete(idx); else flagged.add(idx);
    persist(); syncNav();
  });
  $('reviewBtn').addEventListener('click', function () { showReview(false); });
  submitBtn.addEventListener('click', function (e) { e.preventDefault(); showReview(true); });
  form.addEventListener('submit', function (e) { if (!submitting) { e.preventDefault(); showReview(true); } });

  function chipRow(label, nums, cls) {
    var p = document.createElement('div'); p.className = 'review-row';
    var s = document.createElement('div'); s.className = 'review-label'; s.textContent = label; p.appendChild(s);
    var wrap = document.createElement('div'); wrap.className = 'review-chips';
    nums.forEach(function (n) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'btn btn-sm ' + cls;
      b.textContent = String(n); b.setAttribute('aria-label', 'Go to question ' + n);
      b.addEventListener('click', function () { modal().hide(); go(n - 1); });
      wrap.appendChild(b);
    });
    p.appendChild(wrap);
    return p;
  }
  var _modal;
  function modal() { return _modal || (_modal = new bootstrap.Modal($('reviewModal'))); }
  function showReview(fromSubmit) {
    var unanswered = [], fl = Array.from(flagged).map(function (i) { return i + 1; }).sort(function (a, b) { return a - b; });
    questions.forEach(function (_, i) { if (!isAns(i)) unanswered.push(i + 1); });
    var body = $('reviewBody'); body.textContent = '';
    var sum = document.createElement('p'); sum.className = 'review-sum';
    sum.textContent = answeredCount() + ' of ' + questions.length + ' answered.';
    body.appendChild(sum);
    if (unanswered.length) body.appendChild(chipRow(unanswered.length + ' unanswered', unanswered, 'btn-outline-navy'));
    else { var ok = document.createElement('p'); ok.className = 'text-success mb-2'; ok.innerHTML = '<i class="bi bi-check-circle" aria-hidden="true"></i> '; ok.append('Every question has an answer.'); body.appendChild(ok); }
    if (fl.length) body.appendChild(chipRow('Flagged for review', fl, 'btn-outline-gold'));
    if (fromSubmit && unanswered.length) {
      var w = document.createElement('p'); w.className = 'small text-muted mb-0';
      w.textContent = 'Unanswered questions are marked wrong.'; body.appendChild(w);
    }
    var c = $('confirmSubmit');
    c.classList.toggle('d-none', !fromSubmit);
    c.textContent = unanswered.length ? (cfg.submitAnyway || 'Submit anyway') : (cfg.submitLabel || 'Submit');
    $('reviewTitle').textContent = fromSubmit ? 'Ready to submit?' : 'Review your answers';
    modal().show();
  }
  $('confirmSubmit').addEventListener('click', function () { doSubmit(false); });

  // Keyboard shortcuts outside inputs: ←/→ move, F flags
  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target; if (t && (t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'radio') || t.tagName === 'SELECT')) return;
    if (document.querySelector('.modal.show')) return;
    if (e.key === 'ArrowRight' && t.type !== 'radio') { go(idx + 1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft' && t.type !== 'radio') { go(idx - 1); e.preventDefault(); }
    else if (e.key === 'f' || e.key === 'F') { flagBtn.click(); }
  });

  window.addEventListener('beforeunload', function (e) {
    if (submitting || !answeredCount()) return;
    e.preventDefault(); e.returnValue = '';
  });

  var reportBtn = $('reportQBtn');
  if (reportBtn) reportBtn.addEventListener('click', function () {
    var q = questions[idx] || {};
    var params = new URLSearchParams(JSON.parse(cfg.reportParams || '{}'));
    params.set('quote', 'Q' + (idx + 1) + '. ' + (q.text || ''));
    window.open(cfg.reportUrl + '?' + params.toString(), '_blank', 'noopener');
  });

  // Countdown (tests only)
  if (cfg.remaining) {
    var endAt = Date.now() + parseInt(cfg.remaining, 10) * 1000;
    var timerEl = $('testTimer'), disp = $('timerDisplay'), ban = $('timeWarnBanner');
    var said = {};
    var say = function (k, cls, msg) { if (said[k]) return; said[k] = 1; if (ban) { ban.className = 'show ' + cls; ban.textContent = msg; } };
    var tick = function () {
      var ms = endAt - Date.now();
      if (ms <= 0) {
        disp.textContent = '0:00'; timerEl.className = 'test-timer danger';
        say('up', 'danger', 'Time is up. Submitting and grading your answers now.');
        doSubmit(true); return;
      }
      var s = Math.floor(ms / 1000), m = Math.floor(s / 60);
      disp.textContent = m + ':' + String(s % 60).padStart(2, '0');
      timerEl.setAttribute('aria-label', m + ' minutes ' + (s % 60) + ' seconds left');
      var cls = s <= 60 ? 'danger' : s <= 300 ? 'warn5' : s <= 900 ? 'warn10' : 'ok';
      timerEl.className = 'test-timer ' + cls;
      if (s <= 60) say('1', 'danger', 'Less than 1 minute left. The test submits itself at zero.');
      else if (s <= 300) say('5', 'warn5', '5 minutes left. Check flagged items and submit soon.');
      else if (s <= 600) say('10', 'warn10', '10 minutes left. Check unanswered and flagged questions.');
      else if (s <= 900) say('15', 'warn10', '15 minutes left. Plan your last pass now.');
    };
    tick(); setInterval(tick, 1000);
  }

  buildNav();
  // resume on the first unanswered question after a reload
  if (answeredCount()) { for (var i = 0; i < questions.length; i++) { if (!isAns(i)) { idx = i; break; } } }
  render(false);
  if (answeredCount() && live) live.textContent = 'Your saved answers were restored.';
})();
