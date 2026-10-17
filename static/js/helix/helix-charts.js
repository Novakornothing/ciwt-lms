/* Helix instructor charts: AOI swimlane timelines (SVG), lesson heatmap
   (canvas), and matrix colouring. Data comes from <script type="application/json">. */
(function () {
  'use strict';
  var STATE_COLORS = { off_page: '#9aa9bc', chrome: '#c3ccd8', _face_lost: '#e5484d', _hidden: '#6e56cf',
                       _low_conf: '#f0b429', _idle: '#b7c2cf', _paused: '#d5dbe3' };
  function aoiColor(i, n) {
    var h = (195 + i * (300 / Math.max(1, n))) % 360;
    return 'hsl(' + Math.round(h) + ',62%,' + (i % 2 ? 46 : 38) + '%)';
  }
  function data(id) { var n = document.getElementById(id); if (!n) return null; try { return JSON.parse(n.textContent); } catch (e) { return null; } }
  function fmt(ms) { var s = Math.round(ms / 1000); return s >= 60 ? Math.floor(s / 60) + 'm ' + (s % 60) + 's' : s + 's'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }

  function colorMap(lanes) {
    var labels = [];
    lanes.forEach(function (l) { l.segments.forEach(function (s) { if (!STATE_COLORS[s[2]] && labels.indexOf(s[3]) < 0) labels.push(s[3]); }); });
    var map = {};
    labels.forEach(function (lab, i) { map[lab] = aoiColor(i, labels.length); });
    return map;
  }

  function renderLanes(host) {
    var lanes = data(host.getAttribute('data-src'));
    if (!lanes || !lanes.length) { host.innerHTML = '<p class="text-muted small mb-0">No timelines recorded yet.</p>'; return; }
    var cmap = colorMap(lanes);
    var maxDur = Math.max.apply(null, lanes.map(function (l) { return l.duration_ms || 1; }));
    var common = host.getAttribute('data-scale') !== 'each';
    var html = '';
    lanes.forEach(function (l) {
      var dur = common ? maxDur : (l.duration_ms || 1);
      var rects = l.segments.map(function (s) {
        var x = s[0] / dur * 1000, w = Math.max(0.8, (s[1] - s[0]) / dur * 1000);
        var c = STATE_COLORS[s[2]] || cmap[s[3]] || '#3ec7ff';
        return '<rect x="' + x.toFixed(1) + '" y="0" width="' + w.toFixed(1) + '" height="22" fill="' + c + '"><title>' +
          esc(s[3]) + ' · ' + fmt(s[1] - s[0]) + ' (at ' + fmt(s[0]) + ')</title></rect>';
      }).join('');
      var label = esc(l.name) + (l.started ? ' <span class="text-muted">· ' + esc(l.started) + '</span>' : '');
      html += '<div class="hx-lane"><div class="hx-lane-label" title="' + esc(l.name) + '">' + label + '</div>' +
        '<svg viewBox="0 0 1000 22" preserveAspectRatio="none" role="img" aria-label="Timeline for ' + esc(l.name) + ', ' + fmt(l.duration_ms) + '">' + rects + '</svg></div>';
    });
    var ticks = [0, .25, .5, .75, 1].map(function (f) { return '<span>' + fmt(maxDur * f) + '</span>'; }).join('');
    html += '<div class="hx-axis"><div></div><div>' + ticks + '</div></div>';
    var legend = Object.keys(cmap).slice(0, 14).map(function (k) { return '<span><i style="background:' + cmap[k] + '"></i>' + esc(k) + '</span>'; }).join('');
    legend += '<span><i style="background:#9aa9bc"></i>Looking away</span><span><i style="background:#e5484d"></i>Face not detected</span>' +
      '<span><i style="background:#6e56cf"></i>Tab hidden</span><span><i style="background:#f0b429"></i>Low confidence</span><span><i style="background:#d5dbe3"></i>Paused / idle</span>';
    html += '<div class="hx-legend mt-2">' + legend + '</div>';
    host.innerHTML = html;
  }

  function heatColor(v) {
    // dark navy -> teal -> yellow -> white
    var stops = [[10, 20, 36], [20, 110, 140], [62, 199, 255], [240, 193, 75], [255, 250, 230]];
    var t = Math.max(0, Math.min(1, v)) * (stops.length - 1);
    var i = Math.min(stops.length - 2, Math.floor(t)), f = t - i;
    var a = stops[i], b = stops[i + 1];
    return 'rgb(' + [0, 1, 2].map(function (k) { return Math.round(a[k] + (b[k] - a[k]) * f); }).join(',') + ')';
  }

  function renderHeat(canvas) {
    var d = data(canvas.getAttribute('data-src'));
    if (!d) return;
    var heat = d.heat, layout = d.layout || [];
    var dpr = window.devicePixelRatio || 1;
    var W = canvas.clientWidth || 200, H = canvas.clientHeight || 480;
    canvas.width = W * dpr; canvas.height = H * dpr;
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.fillStyle = heatColor(0); ctx.fillRect(0, 0, W, H);
    // low-res offscreen then upscale with blur for a smooth heatmap
    var off = document.createElement('canvas');
    off.width = heat.cols; off.height = heat.rows;
    var o = off.getContext('2d');
    for (var y = 0; y < heat.rows; y++) for (var x = 0; x < heat.cols; x++) {
      var v = heat.grid[y][x];
      o.fillStyle = heatColor(Math.sqrt(v)); o.fillRect(x, y, 1, 1);
    }
    ctx.imageSmoothingEnabled = true;
    if ('filter' in ctx) ctx.filter = 'blur(' + Math.max(2, W / 60) + 'px)';
    ctx.drawImage(off, 0, 0, W, H);
    ctx.filter = 'none';
    // AOI boundaries
    ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.font = '600 10px system-ui, sans-serif';
    layout.filter(function (a) { return a.kind === 'heading'; }).forEach(function (a, i) {
      var yy = Math.round(a.y0 * H) + .5;
      ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(W, yy); ctx.stroke();
      ctx.fillText(String(i + 1), 4, yy + 11);
    });
    canvas.setAttribute('aria-label', 'Heatmap of gaze across the lesson page from ' + (heat.sessions || 0) + ' sessions; brighter means more dwell.');
  }

  function shadeMatrix(table) {
    table.querySelectorAll('td.hx-cell').forEach(function (td) {
      var v = parseFloat(td.getAttribute('data-share') || '0') / 100;
      var mean = parseFloat(td.getAttribute('data-mean') || '0') / 100;
      var a = Math.min(1, v / Math.max(0.05, mean * 2));
      td.style.background = 'rgba(31,157,107,' + (0.08 + a * 0.75).toFixed(2) + ')';
      if (a > 0.7) td.style.color = '#fff';
    });
  }

  function init() {
    document.querySelectorAll('[data-hx-lanes]').forEach(renderLanes);
    document.querySelectorAll('canvas[data-hx-heat]').forEach(renderHeat);
    document.querySelectorAll('table.hx-matrix').forEach(shadeMatrix);
  }
  var rt;
  window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { document.querySelectorAll('canvas[data-hx-heat]').forEach(renderHeat); }, 200); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.HelixCharts = { init: init, heatColor: heatColor };
})();
