/* Inline AI tutor drawer (Priority 3). Builds the answer with DOM methods only (no innerHTML from the server). */
(function () {
  var d = document.getElementById('tutor-drawer'), open = document.getElementById('tutor-open');
  if (!d || !open) return;
  var out = document.getElementById('tutor-out'), q = document.getElementById('tutor-dq');
  var tok = (document.querySelector('meta[name="csrf-token"]') || {}).content || '';
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function toggle(show) { d.hidden = !show; open.setAttribute('aria-expanded', show ? 'true' : 'false'); if (show) q.focus(); else open.focus(); }
  open.addEventListener('click', function () { toggle(d.hidden); });
  document.getElementById('tutor-close').addEventListener('click', function () { toggle(false); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') toggle(false); });
  document.getElementById('tutor-form').addEventListener('submit', function (e) {
    e.preventDefault();
    out.textContent = 'Looking in your course…';
    fetch(d.dataset.url, { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': tok, 'X-Requested-With': 'fetch' },
      body: JSON.stringify({ q: q.value, section_id: d.dataset.section }) })
      .then(function (r) { return r.json(); })
      .then(function (r) {
        out.textContent = '';
        if (r.error) { out.textContent = r.error; return; }
        out.appendChild(el('div', 'tutor-answer' + (r.outcome === 'answered' ? '' : ' tutor-refusal'), r.answer));
        if (r.cites && r.cites.length) {
          var ol = el('ol', 'tutor-cites mt-2');
          r.cites.forEach(function (c) {
            var li = el('li'), kind = c.type === 'rung' ? 'Explanation · ' + c.kind : c.type === 'lesson' ? 'Lesson section' : c.type === 'lab' ? 'Lab guide' : 'Glossary';
            li.appendChild(el('span', 'tutor-kind d-block text-body-secondary', kind));
            var t = (c.label ? c.label + ' — ' : '') + c.title;
            if (c.url) { var a = el('a', '', t); a.href = c.url; li.appendChild(a); } else li.appendChild(el('span', '', t));
            ol.appendChild(li);
          });
          out.appendChild(ol);
        }
        if (r.glossary && r.glossary.length) out.appendChild(el('p', 'small mb-0', 'Glossary: ' + r.glossary.map(function (g) { return g.term; }).join(', ')));
      })
      .catch(function () { out.textContent = 'The tutor could not be reached. Try again.'; });
  });
})();
