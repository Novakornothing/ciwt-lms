/* Mastery (pass 11): in-lesson quick check. Measures how long each lesson section is on screen (only while
   this tab is visible; kept in the page, sent only with a quick-check answer) and shows the server's reply
   inline. A miss after a long stay (or Helix re-reads, with consent) brings an optional alternate explanation. */
(function () {
  var body = document.getElementById('lessonBody');
  var forms = document.querySelectorAll('.mx-quick-form');
  if (!body || !forms.length) return;
  var tok = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  var dwell = {}, visible = {}, last = Date.now();
  var norm = function (s) { return (s || '').replace(/\s+/g, ' ').trim(); };
  var heads = Array.prototype.slice.call(body.querySelectorAll('h3'));
  function tick() {
    var now = Date.now(), dt = now - last; last = now;
    if (document.visibilityState !== 'visible') return;
    Object.keys(visible).forEach(function (k) { if (visible[k]) dwell[k] = (dwell[k] || 0) + dt; });
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      tick();
      entries.forEach(function (e) { visible[e.target.getAttribute('data-mx-head')] = e.isIntersecting; });
    }, { threshold: 0.25 });
    heads.forEach(function (h) {
      var sec = h.closest('section') || h.parentElement;
      sec.setAttribute('data-mx-head', norm(h.textContent));
      io.observe(sec);
    });
  }
  setInterval(tick, 1000);
  document.addEventListener('visibilitychange', tick);

  function wireDismiss(box) {
    var b = box.querySelector('[data-mx-dismiss]');
    if (!b) return;
    b.addEventListener('click', function () {
      fetch(b.getAttribute('data-mx-dismiss'), { method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': tok }, body: '{}' }).catch(function () {});
      var region = box.querySelector('.mx-struggle');
      if (region) region.remove();
      box.insertAdjacentHTML('beforeend', '<p class="small mb-0">Dismissed. It will not come back for this question.</p>');
      box.focus();
    });
  }
  Array.prototype.forEach.call(forms, function (f) {
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      tick();
      var picked = f.querySelector('input[name="answer"]:checked');
      var out = f.querySelector('.mx-quick-result');
      if (!picked) { out.textContent = 'Choose one of the answers first.'; return; }
      var head = norm(f.getAttribute('data-heading'));
      var btn = f.querySelector('button[type="submit"]');
      btn.disabled = true;
      fetch(f.action, { method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': tok },
        body: JSON.stringify({ answer: picked.value, heading: head, dwell_ms: Math.round(dwell[head] || 0) }) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          out.innerHTML = j.html || '';
          out.setAttribute('tabindex', '-1');
          if (j.ok) Array.prototype.forEach.call(f.querySelectorAll('input[name="answer"]'), function (i) { i.disabled = true; });
          else btn.disabled = false;
          wireDismiss(out);
          if (j.offer) out.focus();
        })
        .catch(function () { btn.disabled = false; out.textContent = 'Could not check that right now. Try again.'; });
    });
  });
})();
