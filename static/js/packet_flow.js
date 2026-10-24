/* Packet / Frame Walk (Option B pass 1). Reads /labs/<id>/packet-flow, draws the topology and steps hop by hop. */
(function () {
  'use strict';
  var root = document.getElementById('packetFlow');
  if (!root) return;
  var NS = 'http://www.w3.org/2000/svg';
  var svg = document.getElementById('pfSvg'), list = document.getElementById('pfHops'), sum = document.getElementById('pfSummary');
  var names = ['Client PC', 'Switch', 'Router', 'DNS / Server'];
  var data = null, shown = 0;
  function el(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (text) e.textContent = text;
    return e;
  }
  function draw() {
    while (svg.lastChild && svg.lastChild.tagName !== 'title') svg.removeChild(svg.lastChild);
    for (var i = 0; i < 4; i++) {
      var x = 20 + i * 120;
      if (i < 3) {
        var st = !data || i >= shown ? 'pf-link' : (data.hops[Math.min(i + 1, data.hops.length) - 1] || {}).ok === false ? 'pf-link pf-bad' : 'pf-link pf-ok';
        if (data && i + 1 > data.hops.length && shown > data.hops.length - 1 && !data.ok) st = 'pf-link pf-cut';
        svg.appendChild(el('line', {x1: x + 30, y1: 35, x2: x + 110, y2: 35, 'class': st}));
      }
      svg.appendChild(el('rect', {x: x - 10, y: 18, width: 60, height: 34, rx: 6, 'class': 'pf-node'}));
      svg.appendChild(el('text', {x: x + 20, y: 72, 'text-anchor': 'middle', 'class': 'pf-label'}, names[i]));
    }
    if (data && shown) {
      var h = data.hops[shown - 1], cx = 20 + Math.min(shown, 3) * 120 - (h.ok ? 0 : 60) + 20;
      svg.appendChild(el('circle', {cx: cx, cy: 35, r: 7, 'class': h.ok ? 'pf-dot pf-dot-ok' : 'pf-dot pf-dot-bad'}));
    }
  }
  function render() {
    list.innerHTML = '';
    (data ? data.hops.slice(0, shown) : []).forEach(function (h) {
      var li = document.createElement('li');
      li.className = h.ok ? 'pf-ok-text' : 'pf-bad-text';
      li.textContent = (h.ok ? '✓ ' : '✗ ') + 'Hop ' + h.n + ': ' + h.label + ' — ' + h.detail;
      list.appendChild(li);
    });
    sum.textContent = data && shown >= data.hops.length ? data.packet + ': ' + data.summary : '';
    draw();
  }
  function load(cb) {
    var t = document.getElementById('pfType').value;
    fetch(root.dataset.url + '?type=' + encodeURIComponent(t), {credentials: 'same-origin'})
      .then(function (r) { return r.json(); }).then(function (j) { data = j; shown = 0; cb(); });
  }
  function animate() {
    if (!data || shown >= data.hops.length) return;
    shown++; render();
    if (shown < data.hops.length) setTimeout(animate, window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 600);
  }
  document.getElementById('pfTrace').addEventListener('click', function () { load(animate); });
  document.getElementById('pfStep').addEventListener('click', function () {
    if (!data || shown >= data.hops.length) load(function () { shown = 1; render(); }); else { shown++; render(); }
  });
  draw();
})();
