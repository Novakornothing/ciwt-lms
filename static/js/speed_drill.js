/* Speed-Drill (Option B pass 4): 60-second Blitz with streak, instant feedback and a missed-card retry queue, and
   Flip-Card study with Got it / Review again. Every answer is recorded for spaced repetition. */
(function () {
  'use strict';
  var root = document.getElementById('speedDrill');
  if (!root) return;
  var cards = JSON.parse(document.getElementById('sdData').textContent || '[]');
  var csrfEl = document.querySelector('meta[name="csrf-token"]') || document.querySelector('input[name="csrf_token"]');
  var csrf = csrfEl ? (csrfEl.content || csrfEl.value) : '';
  var $ = function (id) { return document.getElementById(id); };
  var mode = 'blitz', i = 0, left = 0, timer = null, streak = 0, score = 0, retry = [], cur = null, running = false;

  function record(card, result) {
    fetch(root.dataset.record, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify({ card: card.id, result: result, streak: streak })
    }).catch(function () { /* offline: the drill keeps going */ });
  }
  function next() {
    if (retry.length && (i % 4 === 3 || i >= cards.length)) cur = retry.shift();
    else if (i < cards.length) cur = cards[i++];
    else { cur = null; }
    $('sdRetry').textContent = retry.length;
    if (!cur) { finish('Deck complete.'); return; }
    $('sdCatLbl').textContent = cur.cat + ' · ' + cur.codes.join(', ');
    $('sdFront').textContent = cur.front;
    $('sdFeedback').textContent = '';
    if (mode === 'blitz') {
      var box = $('sdChoices'); box.innerHTML = '';
      cur.choices.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button'; b.className = 'btn btn-outline-secondary sd-choice'; b.textContent = c;
        b.addEventListener('click', function () { answer(b, c); });
        box.appendChild(b);
      });
    } else {
      $('sdBack').textContent = cur.back;
      $('sdBack').classList.add('d-none');
    }
  }
  function answer(btn, c) {
    if (!running) return;
    var ok = c === cur.back;
    Array.prototype.forEach.call(document.querySelectorAll('.sd-choice'), function (b) {
      b.disabled = true;
      if (b.textContent === cur.back) b.classList.add('sd-right');
    });
    if (!ok) { btn.classList.add('sd-wrong'); retry.push(cur); streak = 0; } else { streak += 1; score += 1; }
    $('sdStreak').textContent = streak; $('sdScore').textContent = score;
    $('sdFeedback').textContent = ok ? 'Correct.' : 'Missed — ' + cur.front + ' = ' + cur.back + ' (queued for retry).';
    record(cur, ok ? 'right' : 'wrong');
    setTimeout(next, ok ? 450 : 1300);
  }
  function finish(msg) {
    running = false; clearInterval(timer);
    $('sdChoices').innerHTML = '';
    $('sdFront').textContent = msg + ' Score ' + score + ', streak ' + streak + '. Press Start for another round.';
    $('sdStart').classList.remove('d-none');
  }
  function start() {
    running = true; i = 0; streak = 0; score = 0; retry = [];
    $('sdStreak').textContent = 0; $('sdScore').textContent = 0;
    $('sdStart').classList.add('d-none');
    if (mode === 'blitz') {
      left = parseInt(root.dataset.seconds, 10) || 60; $('sdClock').textContent = left;
      clearInterval(timer);
      timer = setInterval(function () { left -= 1; $('sdClock').textContent = Math.max(0, left); if (left <= 0) finish('Time!'); }, 1000);
    }
    next();
  }
  function setMode(m) {
    mode = m; running = false; clearInterval(timer);
    $('sdModeBlitz').setAttribute('aria-pressed', m === 'blitz' ? 'true' : 'false');
    $('sdModeFlip').setAttribute('aria-pressed', m === 'flip' ? 'true' : 'false');
    $('sdModeBlitz').className = 'btn ' + (m === 'blitz' ? 'btn-navy' : 'btn-outline-navy');
    $('sdModeFlip').className = 'btn ' + (m === 'flip' ? 'btn-navy' : 'btn-outline-navy');
    $('sdChoices').classList.toggle('d-none', m !== 'blitz');
    $('sdFlip').classList.toggle('d-none', m !== 'flip');
    $('sdFront').textContent = 'Press Start to begin.';
    $('sdStart').classList.remove('d-none');
  }
  $('sdModeBlitz').addEventListener('click', function () { setMode('blitz'); });
  $('sdModeFlip').addEventListener('click', function () { setMode('flip'); });
  $('sdStart').addEventListener('click', start);
  $('sdShow').addEventListener('click', function () { $('sdBack').classList.remove('d-none'); });
  $('sdGot').addEventListener('click', function () {
    if (!cur || !running) return; streak += 1; score += 1; record(cur, 'got');
    $('sdStreak').textContent = streak; $('sdScore').textContent = score; next();
  });
  $('sdAgain').addEventListener('click', function () {
    if (!cur || !running) return; streak = 0; retry.push(cur); record(cur, 'again');
    $('sdStreak').textContent = 0; next();
  });
})();
