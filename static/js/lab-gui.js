/* Novak LMS live labs — Windows 11 desktop simulator.
 * The server owns the desktop state (open window, Settings page, adapter, Active Directory). Every click is an
 * event POSTed to /labs/<id>/event; the reply re-renders the window, so a reload restores the same place.
 * Touch: 44px targets, long-press = right-click, narrow layout (Settings nav collapses behind a Back button),
 * portrait and landscape. */
(function () {
  'use strict';
  var cfg = LabKit.config();
  if (!cfg) return;
  var kit = LabKit.init(cfg);
  var el = LabKit.el;
  var desk = document.getElementById('w11Desk');
  var winHost = document.getElementById('w11Win');
  var startMenu = document.getElementById('w11Start');
  var startBtn = document.getElementById('w11StartBtn');
  var search = document.getElementById('w11Search');
  var ctx = document.getElementById('w11Ctx');
  var facts = cfg.boot.facts || {};
  var gui = cfg.boot.gui || {};
  var hasAD = !!gui.ad;
  var selUser = null, selOU = 'Sales', dialog = null, status = '';

  var APPS = [
    { id: 'settings', name: 'Settings', icon: 'bi-gear', keys: 'settings ms-settings win+i control panel' },
    { id: 'services', name: 'Services', icon: 'bi-list-check', keys: 'services services.msc' },
    { id: 'devmgr', name: 'Device Manager', icon: 'bi-cpu', keys: 'device manager devmgmt.msc drivers' },
    { id: 'ncpa', name: 'Network Connections', icon: 'bi-ethernet', keys: 'network connections ncpa.cpl adapter' }
  ];
  if (hasAD) APPS.push({ id: 'aduc', name: 'Active Directory Users and Computers', icon: 'bi-people', keys: 'active directory users computers dsa dsa.msc aduc' });

  function send(ev, data) {
    return kit.post(cfg.urls.event, { ev: ev, data: data || {} }).then(function (p) {
      var r = p.result || {};
      if (r.error && r.error !== 'unknown event') { status = r.error; kit.toast(r.error, 'error'); kit.say(r.error); }
      else if (r.ok) { status = r.ok; kit.say(r.ok); }
      kit.apply(p);
      return p;
    });
  }

  kit.on(function (p) { if (p.gui) { gui = p.gui; render(); } });
  kit.onUndo = function () { render(); };

  /* ---------------- desktop + start menu */
  document.querySelectorAll('[data-app]').forEach(function (b) {
    b.addEventListener('click', function () { closeStart(); dialog = null; status = ''; send('open:' + b.getAttribute('data-app')); });
  });
  function openStart() { startMenu.hidden = false; startBtn.setAttribute('aria-expanded', 'true'); search.value = ''; filter(); setTimeout(function () { search.focus(); }, 30); }
  function closeStart() { startMenu.hidden = true; startBtn.setAttribute('aria-expanded', 'false'); }
  startBtn.addEventListener('click', function () { if (startMenu.hidden) openStart(); else closeStart(); });
  function filter() {
    var q = search.value.trim().toLowerCase();
    var list = document.getElementById('w11StartList');
    list.innerHTML = '';
    APPS.filter(function (a) { return !q || a.keys.indexOf(q) >= 0 || a.name.toLowerCase().indexOf(q) >= 0; }).forEach(function (a) {
      var b = el('button', { type: 'button', class: 'w11-start-item', 'data-start': a.id }, [el('i', { class: 'bi ' + a.icon, 'aria-hidden': 'true' }), el('span', { text: a.name })]);
      b.addEventListener('click', function () { closeStart(); dialog = null; status = ''; send('open:' + a.id); });
      list.appendChild(b);
    });
    if (!list.children.length) list.appendChild(el('p', { class: 'small px-2 mb-0', text: 'No apps match "' + q + '". Try settings, services.msc, devmgmt.msc, ncpa.cpl' + (hasAD ? ' or dsa.msc' : '') + '.' }));
  }
  search.addEventListener('input', filter);
  search.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { var f = document.querySelector('#w11StartList [data-start]'); if (f) f.click(); }
    if (e.key === 'Escape') { closeStart(); startBtn.focus(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { if (!startMenu.hidden) closeStart(); hideCtx(); }
  });
  desk.addEventListener('click', function (e) { if (!e.target.closest('.w11-start, #w11StartBtn')) closeStart(); if (!e.target.closest('.w11-ctx')) hideCtx(); });

  /* ---------------- context menu: right-click and long-press */
  function showCtx(x, y, items) {
    ctx.innerHTML = '';
    items.forEach(function (it) {
      var b = el('button', { type: 'button', role: 'menuitem', class: 'w11-ctx-item', text: it.label, disabled: it.disabled });
      b.addEventListener('click', function () { hideCtx(); it.run(); });
      ctx.appendChild(b);
    });
    var r = desk.getBoundingClientRect();
    ctx.hidden = false;
    var w = ctx.offsetWidth, h = ctx.offsetHeight;
    ctx.style.left = Math.max(4, Math.min(x - r.left, r.width - w - 4)) + 'px';
    ctx.style.top = Math.max(4, Math.min(y - r.top, r.height - h - 4)) + 'px';
    var f = ctx.querySelector('button:not([disabled])'); if (f) f.focus();
  }
  function hideCtx() { ctx.hidden = true; }
  function longPress(node, getItems) {
    var t = null, sx = 0, sy = 0;
    node.addEventListener('contextmenu', function (e) { e.preventDefault(); showCtx(e.clientX, e.clientY, getItems()); });
    node.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse') return;
      sx = e.clientX; sy = e.clientY;
      t = setTimeout(function () { t = null; node._lp = true; showCtx(sx, sy, getItems()); if (navigator.vibrate) navigator.vibrate(15); }, 550);
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (n) { node.addEventListener(n, function () { if (t) { clearTimeout(t); t = null; } }); });
    node.addEventListener('pointermove', function (e) { if (t && Math.abs(e.clientX - sx) + Math.abs(e.clientY - sy) > 10) { clearTimeout(t); t = null; } });
    node.addEventListener('click', function (e) { if (node._lp) { node._lp = false; e.preventDefault(); e.stopImmediatePropagation(); } }, true);
    node.addEventListener('keydown', function (e) {
      if (e.key === 'ContextMenu' || (e.shiftKey && e.key === 'F10')) { e.preventDefault(); var r = node.getBoundingClientRect(); showCtx(r.left + 20, r.bottom - 4, getItems()); }
    });
  }

  /* ---------------- window chrome */
  function frame(title, icon, content, opts) {
    opts = opts || {};
    var close = el('button', { type: 'button', class: 'w11-close', 'aria-label': 'Close ' + title, html: '<i class="bi bi-x-lg" aria-hidden="true"></i>' });
    close.addEventListener('click', function () { dialog = null; send('close'); });
    var bar = el('div', { class: 'w11-titlebar' }, [
      opts.back ? opts.back : null,
      el('span', { class: 'w11-title' }, [el('i', { class: 'bi ' + icon, 'aria-hidden': 'true' }), ' ' + title]), close]);
    var w = el('div', { class: 'w11-window', role: 'region', 'aria-label': title }, [bar, content]);
    var st = el('div', { class: 'w11-status', role: 'status' });
    st.textContent = status || '';
    w.appendChild(st);
    return w;
  }

  function row(label, sub, ev, opts) {
    opts = opts || {};
    var b = el('button', { type: 'button', class: 'w11-row' + (opts.active ? ' active' : ''), 'data-ev': ev || null, disabled: !ev && !opts.onClick },
      [opts.icon ? el('i', { class: 'bi ' + opts.icon, 'aria-hidden': 'true' }) : null,
        el('span', { class: 'w11-row-text' }, [el('span', { class: 'w11-row-label', text: label }), sub ? el('span', { class: 'w11-row-sub', text: sub }) : null]),
        ev || opts.onClick ? el('i', { class: 'bi bi-chevron-right ms-auto', 'aria-hidden': 'true' }) : null]);
    if (ev) b.addEventListener('click', function () { status = ''; send(ev); });
    if (opts.onClick) b.addEventListener('click', opts.onClick);
    return b;
  }
  function kv(pairs) {
    var dl = el('dl', { class: 'w11-kv' });
    pairs.forEach(function (p) { dl.appendChild(el('dt', { text: p[0] })); dl.appendChild(el('dd', { text: p[1] })); });
    return dl;
  }

  /* ---------------- Settings */
  var NAV = [['home', 'Home', 'bi-house'], ['system', 'System', 'bi-display'], ['network', 'Network & internet', 'bi-wifi'],
    ['accounts', 'Accounts', 'bi-person-circle'], ['update', 'Windows Update', 'bi-arrow-repeat']];
  var PARENT = { about: 'system', display: 'system', sound: 'system', ethernet: 'network', wifi: 'network', vpn: 'network', advanced: 'network' };
  function settings() {
    var pane = gui.pane || 'home';
    var top = PARENT[pane] || pane;
    var nav = el('nav', { class: 'w11-nav', 'aria-label': 'Settings' });
    NAV.forEach(function (n) {
      var b = el('button', { type: 'button', class: 'w11-nav-item' + (top === n[0] ? ' active' : ''), 'aria-current': top === n[0] ? 'page' : null },
        [el('i', { class: 'bi ' + n[2], 'aria-hidden': 'true' }), el('span', { text: n[1] })]);
      b.addEventListener('click', function () { status = ''; send('pane:' + n[0]); });
      nav.appendChild(b);
    });
    var c = el('div', { class: 'w11-pane' });
    var title = { home: 'Home', system: 'System', about: 'System › About', network: 'Network & internet', ethernet: 'Network & internet › Ethernet',
      advanced: 'Network & internet › Advanced network settings', accounts: 'Accounts', update: 'Windows Update', wifi: 'Network & internet › Wi-Fi',
      vpn: 'Network & internet › VPN', display: 'System › Display', sound: 'System › Sound' }[pane] || pane;
    c.appendChild(el('h3', { class: 'w11-h', text: title }));
    var up = facts.ipv4 && gui.adapter !== 'down';
    if (pane === 'home') {
      c.appendChild(el('p', { class: 'small', text: (facts.hostname || 'PC') + ' · ' + (facts.edition || 'Windows 11') }));
      c.appendChild(row('System', 'Display, sound, About', 'pane:system', { icon: 'bi-display' }));
      c.appendChild(row('Network & internet', up ? 'Ethernet — connected' : 'Ethernet — disabled', 'pane:network', { icon: 'bi-wifi' }));
      c.appendChild(row('Accounts', facts.user || '', 'pane:accounts', { icon: 'bi-person-circle' }));
      c.appendChild(row('Windows Update', 'Check for updates', 'pane:update', { icon: 'bi-arrow-repeat' }));
    } else if (pane === 'system') {
      c.appendChild(row('Display', 'Monitors, brightness, scale', 'pane:display', { icon: 'bi-display' }));
      c.appendChild(row('Sound', 'Volume, output, input', 'pane:sound', { icon: 'bi-volume-up' }));
      c.appendChild(row('About', 'Device specifications, rename this PC, Windows specifications', 'pane:about', { icon: 'bi-info-circle' }));
    } else if (pane === 'about') {
      c.appendChild(el('h4', { class: 'w11-sub', text: 'Device specifications' }));
      c.appendChild(kv([['Device name', facts.hostname], ['Processor', 'Intel(R) Core(TM) i5-1345U'], ['Installed RAM', '16.0 GB'], ['System type', '64-bit operating system, x64-based processor']]));
      c.appendChild(el('h4', { class: 'w11-sub', text: 'Windows specifications' }));
      c.appendChild(kv([['Edition', facts.edition], ['Version', facts.version], ['OS build', facts.build], ['Domain', facts.domain]]));
    } else if (pane === 'network') {
      c.appendChild(row('Ethernet', up ? 'Connected · ' + facts.domain : 'Disabled', 'pane:ethernet', { icon: 'bi-ethernet' }));
      c.appendChild(row('Wi-Fi', 'No Wi-Fi adapter on this VM', 'pane:wifi', { icon: 'bi-wifi' }));
      c.appendChild(row('VPN', 'Add, connect, manage', 'pane:vpn', { icon: 'bi-shield-lock' }));
      c.appendChild(row('Advanced network settings', 'View all network adapters, network reset', 'pane:advanced', { icon: 'bi-hdd-network' }));
    } else if (pane === 'ethernet') {
      c.appendChild(kv([['Status', up ? 'Connected' : 'Disabled'], ['IP assignment', 'Automatic (DHCP)'], ['IPv4 address', up ? facts.ipv4 : '—'],
        ['Subnet mask', up ? facts.mask : '—'], ['IPv4 default gateway', up ? facts.gateway : '—'], ['IPv4 DNS servers', up ? (facts.dns || []).join(', ') : '—'],
        ['Physical address (MAC)', '00-15-5D-0A-1E-47']]));
      c.appendChild(el('p', { class: 'small text-muted', text: 'Windows 11 has no Renew button here. To recycle the lease use Advanced network settings (or ncpa.cpl): Disable, then Enable.' }));
    } else if (pane === 'advanced') {
      var dis = gui.adapter === 'down';
      var card = el('div', { class: 'w11-card' }, [
        el('div', { class: 'w11-card-head' }, [el('i', { class: 'bi bi-ethernet', 'aria-hidden': 'true' }), el('span', { class: 'fw-semibold', text: 'Ethernet' }),
          el('span', { class: 'w11-badge ' + (dis ? 'off' : 'on'), text: dis ? 'Disabled' : 'Connected' })]),
        el('div', { class: 'small', text: 'Microsoft Hyper-V Network Adapter' })]);
      var tb = el('button', { type: 'button', class: 'btn btn-sm ' + (dis ? 'btn-brand' : 'btn-outline-navy'), id: 'w11AdapterToggle', text: dis ? 'Enable' : 'Disable' });
      tb.addEventListener('click', function () { send(dis ? 'adapter:enable' : 'adapter:disable'); });
      card.appendChild(tb);
      c.appendChild(card);
      c.appendChild(row('More network adapter options', 'Opens Network Connections (ncpa.cpl)', 'open:ncpa', { icon: 'bi-box-arrow-up-right' }));
      c.appendChild(row('Network reset', 'Not used in this lab — it removes every adapter', null, { icon: 'bi-exclamation-triangle' }));
    } else if (pane === 'accounts') {
      c.appendChild(kv([['Signed in as', facts.user], ['Account type', 'Domain user · Standard'], ['Domain', facts.domain]]));
      c.appendChild(el('p', { class: 'small text-muted', text: 'Name the account before you reset anything.' }));
    } else if (pane === 'update') {
      var checked = gui.updates === 'checked';
      c.appendChild(el('p', { class: 'w11-big', text: checked ? "You're up to date" : 'Updates available? Check now.' }));
      c.appendChild(el('p', { class: 'small', text: checked ? 'Last checked: today, ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Last checked: 3 days ago' }));
      var cb = el('button', { type: 'button', class: 'btn btn-brand btn-sm', id: 'w11CheckUpdates', text: 'Check for updates' });
      cb.addEventListener('click', function () { cb.disabled = true; cb.textContent = 'Checking…'; setTimeout(function () { send('update:check'); }, 500); });
      c.appendChild(cb);
      c.appendChild(row('Update history', 'Quality, driver and definition updates', null, { icon: 'bi-clock-history' }));
    } else if (pane === 'wifi') {
      c.appendChild(el('p', { class: 'small', text: 'This VM has no wireless adapter. The Wi-Fi lab uses netsh wlan.' }));
    } else if (pane === 'vpn') {
      c.appendChild(el('p', { class: 'small', text: 'No VPN connections configured.' }));
    } else if (pane === 'display') {
      c.appendChild(kv([['Display', '1920 × 1080 (recommended)'], ['Scale', '100%'], ['Orientation', 'Landscape']]));
    } else if (pane === 'sound') {
      c.appendChild(kv([['Output', 'Speakers (Hyper-V audio)'], ['Volume', '40']]));
    }
    var back = null;
    if (pane !== 'home') {
      back = el('button', { type: 'button', class: 'w11-back', 'aria-label': 'Back', html: '<i class="bi bi-arrow-left" aria-hidden="true"></i>' });
      back.addEventListener('click', function () { send('pane:' + (PARENT[pane] || 'home')); });
    }
    var body = el('div', { class: 'w11-settings' + (pane !== 'home' ? ' in-pane' : '') }, [nav, c]);
    return frame('Settings', 'bi-gear', body, { back: back });
  }

  /* ---------------- Services */
  var SVCS = [['Dhcp', 'DHCP Client', 'Running', 'Automatic', 'Registers and updates IP addresses and DNS records for this computer.'],
    ['Dnscache', 'DNS Client', 'Running', 'Automatic (Trigger Start)', 'Caches Domain Name System (DNS) names and registers the full computer name.'],
    ['WinDefend', 'Microsoft Defender Antivirus Service', 'Running', 'Automatic', 'Helps protect users from malware and other potentially unwanted software.'],
    ['Spooler', 'Print Spooler', 'Running', 'Automatic', 'Spools print jobs and handles interaction with the printer.'],
    ['wuauserv', 'Windows Update', 'Running', 'Manual (Trigger Start)', 'Enables the detection, download, and installation of updates.']];
  function services() {
    var list = el('div', { class: 'w11-list', role: 'listbox', 'aria-label': 'Services' });
    SVCS.forEach(function (s) {
      var on = gui.svc === s[0];
      var b = el('button', { type: 'button', role: 'option', 'aria-selected': on ? 'true' : 'false', class: 'w11-svc' + (on ? ' active' : ''), 'data-svc': s[0] },
        [el('span', { class: 'w11-svc-name', text: s[1] }), el('span', { class: 'w11-svc-st', text: s[2] }), el('span', { class: 'w11-svc-type', text: s[3] })]);
      b.addEventListener('click', function () { status = ''; send('svc:' + s[0]); });
      longPress(b, function () {
        return [{ label: 'Properties', run: function () { send('svc:' + s[0]); } },
          { label: 'Restart', run: function () { status = 'Lab is read-only for services: note the status — do not restart a service without a ticket.'; send('svc:' + s[0]); } }];
      });
      list.appendChild(b);
    });
    var det = el('div', { class: 'w11-detail' });
    var cur = SVCS.filter(function (s) { return s[0] === gui.svc; })[0];
    if (cur) {
      det.appendChild(el('h4', { class: 'w11-sub', text: cur[1] }));
      det.appendChild(kv([['Service name', cur[0]], ['Status', cur[2]], ['Startup type', cur[3]]]));
      det.appendChild(el('p', { class: 'small', text: cur[4] }));
    } else det.appendChild(el('p', { class: 'small text-muted', text: 'Select a service to see its status and startup type. Long-press or right-click for more.' }));
    return frame('Services (Local)', 'bi-list-check', el('div', { class: 'w11-split' }, [list, det]));
  }

  /* ---------------- Device Manager */
  var DEV = [['net', 'Network adapters', 'bi-ethernet', ['Microsoft Hyper-V Network Adapter']], ['display', 'Display adapters', 'bi-display', ['Microsoft Hyper-V Video']],
    ['disk', 'Disk drives', 'bi-device-hdd', ['Microsoft Virtual Disk']], ['kbd', 'Keyboards', 'bi-keyboard', ['Standard PS/2 Keyboard']]];
  function devmgr() {
    var tree = el('ul', { class: 'w11-tree', role: 'tree', 'aria-label': facts.hostname || 'Devices' });
    var open = gui.dev_open || [];
    DEV.forEach(function (d) {
      var ex = open.indexOf(d[0]) >= 0;
      var b = el('button', { type: 'button', class: 'w11-tree-node', 'aria-expanded': ex ? 'true' : 'false', 'data-dev': d[0] },
        [el('i', { class: 'bi ' + (ex ? 'bi-chevron-down' : 'bi-chevron-right'), 'aria-hidden': 'true' }), el('i', { class: 'bi ' + d[2], 'aria-hidden': 'true' }), el('span', { text: d[1] })]);
      b.addEventListener('click', function () { send('dev:' + d[0]); });
      var li = el('li', { role: 'treeitem', 'aria-expanded': ex ? 'true' : 'false' }, [b]);
      if (ex) {
        var sub = el('ul', { role: 'group' });
        d[3].forEach(function (n) { sub.appendChild(el('li', { role: 'treeitem', class: 'w11-tree-leaf', text: n })); });
        li.appendChild(sub);
      }
      tree.appendChild(li);
    });
    return frame('Device Manager', 'bi-cpu', el('div', { class: 'w11-pane' }, [el('p', { class: 'small text-muted', text: 'No yellow warnings — every device has a working driver.' }), tree]));
  }

  /* ---------------- Network Connections (ncpa.cpl) */
  function ncpa() {
    var dis = gui.adapter === 'down';
    var tile = el('button', { type: 'button', class: 'w11-adapter' + (dis ? ' off' : ''), id: 'w11Adapter', 'aria-label': 'Ethernet, ' + (dis ? 'disabled' : 'connected') + '. Long-press or right-click for options.' },
      [el('i', { class: 'bi bi-ethernet', 'aria-hidden': 'true' }), el('span', { class: 'w11-row-text' }, [el('span', { class: 'fw-semibold', text: 'Ethernet' }),
        el('span', { class: 'small', text: dis ? 'Disabled' : (facts.domain || 'Network') }), el('span', { class: 'small', text: 'Microsoft Hyper-V Network Adapter' })])]);
    function items() {
      return [{ label: 'Disable', disabled: dis, run: function () { send('adapter:disable'); } }, { label: 'Enable', disabled: !dis, run: function () { send('adapter:enable'); } },
        { label: 'Status', run: function () { kit.toast(dis ? 'Ethernet is disabled.' : 'IPv4: ' + facts.ipv4 + ' · Media state: Enabled', 'ok'); } }];
    }
    longPress(tile, items);
    tile.addEventListener('click', function () { tile.classList.toggle('sel'); bar.hidden = !tile.classList.contains('sel'); });
    var bar = el('div', { class: 'w11-cmdbar', hidden: true }, [
      el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy', id: 'w11NcpaDisable', disabled: dis, text: 'Disable this network device', onclick: function () { send('adapter:disable'); } }),
      el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy', id: 'w11NcpaEnable', disabled: !dis, text: 'Enable this network device', onclick: function () { send('adapter:enable'); } })]);
    return frame('Network Connections', 'bi-ethernet', el('div', { class: 'w11-pane' }, [el('p', { class: 'small text-muted', text: 'Select the adapter for the command bar, or long-press / right-click it.' }), tile, bar]));
  }

  /* ---------------- Active Directory Users and Computers */
  function aduc() {
    var ad = gui.ad || { ous: [], users: [], groups: [] };
    var tree = el('div', { class: 'w11-ous', role: 'listbox', 'aria-label': 'Organizational units in ' + ad.domain });
    ad.ous.forEach(function (ou) {
      var on = ou === selOU;
      var b = el('button', { type: 'button', role: 'option', 'aria-selected': on ? 'true' : 'false', class: 'w11-ou' + (on ? ' active' : ''), 'data-ou': ou },
        [el('i', { class: 'bi bi-folder2', 'aria-hidden': 'true' }), el('span', { text: ou })]);
      b.addEventListener('click', function () { selOU = ou; selUser = null; dialog = null; render(); });
      tree.appendChild(b);
    });
    var users = ad.users.filter(function (u) { return u.ou === selOU; });
    var list = el('div', { class: 'w11-users', role: 'listbox', 'aria-label': 'Users in ' + selOU });
    if (!users.length) list.appendChild(el('p', { class: 'small text-muted p-2 mb-0', text: 'No users in this OU.' }));
    users.forEach(function (u) {
      var on = selUser === u.sam;
      var flags = [!u.enabled ? 'Disabled' : null, u.locked ? 'Locked out' : null].filter(Boolean).join(' · ');
      var b = el('button', { type: 'button', role: 'option', 'aria-selected': on ? 'true' : 'false', class: 'w11-user' + (on ? ' active' : '') + (!u.enabled ? ' off' : ''), 'data-user': u.sam },
        [el('i', { class: 'bi ' + (u.enabled ? 'bi-person' : 'bi-person-x'), 'aria-hidden': 'true' }), el('span', { class: 'w11-row-text' }, [el('span', { class: 'fw-semibold', text: u.name }),
          el('span', { class: 'small', text: u.sam + '@' + ad.domain + (flags ? ' · ' + flags : '') })])]);
      b.addEventListener('click', function () { selUser = u.sam; dialog = null; render(); });
      longPress(b, function () { selUser = u.sam; return userMenu(u); });
      list.appendChild(b);
    });
    var tb = el('div', { class: 'w11-cmdbar' }, [el('button', { type: 'button', class: 'btn btn-sm btn-brand', id: 'adNewUser', text: 'New user', onclick: function () { dialog = 'new'; render(); } })]);
    var u = ad.users.filter(function (x) { return x.sam === selUser; })[0];
    if (u) userMenu(u).forEach(function (m) { tb.appendChild(el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy', 'data-act': m.id, text: m.label, disabled: m.disabled, onclick: m.run })); });
    var det = el('div', { class: 'w11-detail' });
    if (u) {
      det.appendChild(el('h4', { class: 'w11-sub', text: u.name }));
      det.appendChild(kv([['Logon name', u.sam + '@' + ad.domain], ['OU', u.ou], ['Account', u.enabled ? 'Enabled' : 'Disabled'], ['Locked out', u.locked ? 'Yes' : 'No'],
        ['Member of', (u.groups || []).join(', ')], ['Must change password', u.must_change ? 'Yes' : 'No']]));
      if (u.note) det.appendChild(el('p', { class: 'small text-muted', text: u.note }));
    }
    var dlg = dialog ? buildDialog(ad, u) : null;
    if (!dialog) openedDialog = null;
    var body = el('div', { class: 'w11-aduc' }, [el('div', { class: 'w11-aduc-left' }, [el('div', { class: 'w11-sub small', text: ad.domain }), tree]),
      el('div', { class: 'w11-aduc-right' }, [tb, dlg, list, det])]);
    return frame('Active Directory Users and Computers', 'bi-people', body);
  }
  function userMenu(u) {
    return [
      { id: 'group', label: 'Add to a group…', run: function () { dialog = 'group'; render(); } },
      { id: 'reset', label: 'Reset password…', run: function () { dialog = 'reset'; render(); } },
      { id: 'unlock', label: 'Unlock account', disabled: !u.locked, run: function () { send('ad:unlock', { sam: u.sam }); } },
      { id: u.enabled ? 'disable' : 'enable', label: u.enabled ? 'Disable account' : 'Enable account', run: function () { send(u.enabled ? 'ad:disable' : 'ad:enable', { sam: u.sam }); } },
      { id: 'move', label: 'Move…', run: function () { dialog = 'move'; render(); } },
      { id: 'delete', label: 'Delete', run: function () { if (window.confirm('Delete ' + u.name + '?')) send('ad:delete', { sam: u.sam }); } }
    ];
  }
  function field(id, label, type, val) {
    return el('div', { class: 'w11-field' }, [el('label', { for: id, class: 'form-label small', text: label }),
      el('input', { id: id, type: type || 'text', class: 'form-control form-control-sm', value: val || '', autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false' })]);
  }
  function check(id, label, on) {
    return el('div', { class: 'form-check' }, [el('input', { id: id, type: 'checkbox', class: 'form-check-input', checked: on }), el('label', { for: id, class: 'form-check-label small', text: label })]);
  }
  function select(id, label, opts) {
    var s = el('select', { id: id, class: 'form-select form-select-sm' });
    opts.forEach(function (o) { s.appendChild(el('option', { value: o, text: o })); });
    return el('div', { class: 'w11-field' }, [el('label', { for: id, class: 'form-label small', text: label }), s]);
  }
  function v(id) { var n = document.getElementById(id); return n ? (n.type === 'checkbox' ? n.checked : n.value) : ''; }
  var openedDialog = null;
  function buildDialog(ad, u) {
    var box = el('div', { class: 'w11-dialog', role: 'dialog', 'aria-modal': 'false', 'aria-labelledby': 'dlgTitle' });
    var cancel = el('button', { type: 'button', class: 'btn btn-sm btn-outline-navy', text: 'Cancel', onclick: function () { dialog = null; render(); } });
    function ok(label, fn) { return el('button', { type: 'button', class: 'btn btn-sm btn-brand', id: 'dlgOk', text: label, onclick: fn }); }
    var done = function (p) { if (!(p.result || {}).error) { dialog = null; render(); } };
    if (dialog === 'new') {
      box.appendChild(el('h4', { class: 'w11-sub', id: 'dlgTitle', text: 'New Object — User (in ' + selOU + ')' }));
      [field('nuFirst', 'First name'), field('nuLast', 'Last name'), field('nuSam', 'User logon name'), field('nuPw', 'Password', 'password'),
        field('nuPw2', 'Confirm password', 'password'), check('nuMust', 'User must change password at next logon', true)].forEach(function (n) { box.appendChild(n); });
      box.appendChild(el('div', { class: 'w11-dlg-actions' }, [ok('Create', function () {
        send('ad:create', { first: v('nuFirst'), last: v('nuLast'), sam: v('nuSam'), ou: selOU, password: v('nuPw'), confirm: v('nuPw2'), must_change: v('nuMust') })
          .then(function (p) { if (!(p.result || {}).error) { selUser = (v('nuSam') || '').toLowerCase(); } done(p); });
      }), cancel]));
    } else if (dialog === 'group' && u) {
      box.appendChild(el('h4', { class: 'w11-sub', id: 'dlgTitle', text: 'Add ' + u.name + ' to a group' }));
      box.appendChild(select('grpSel', 'Group', ad.groups.filter(function (g) { return (u.groups || []).indexOf(g) < 0; })));
      box.appendChild(el('div', { class: 'w11-dlg-actions' }, [ok('Add', function () { send('ad:addgroup', { sam: u.sam, group: v('grpSel') }).then(done); }), cancel]));
    } else if (dialog === 'reset' && u) {
      box.appendChild(el('h4', { class: 'w11-sub', id: 'dlgTitle', text: 'Reset password — ' + u.name }));
      [field('rpPw', 'New password', 'password'), field('rpPw2', 'Confirm password', 'password'), check('rpMust', 'User must change password at next logon', true),
        check('rpUnlock', "Unlock the user's account", !!u.locked)].forEach(function (n) { box.appendChild(n); });
      box.appendChild(el('div', { class: 'w11-dlg-actions' }, [ok('OK', function () {
        send('ad:reset', { sam: u.sam, password: v('rpPw'), confirm: v('rpPw2'), must_change: v('rpMust'), unlock: v('rpUnlock') }).then(done);
      }), cancel]));
    } else if (dialog === 'move' && u) {
      box.appendChild(el('h4', { class: 'w11-sub', id: 'dlgTitle', text: 'Move ' + u.name }));
      box.appendChild(select('mvSel', 'Move to OU', ad.ous));
      box.appendChild(el('div', { class: 'w11-dlg-actions' }, [ok('OK', function () { send('ad:move', { sam: u.sam, ou: v('mvSel') }).then(function (p) { selOU = v('mvSel') || selOU; done(p); }); }), cancel]));
    } else return null;
    if (openedDialog !== dialog) {   // focus the first field only when the dialog first opens, never on re-render
      openedDialog = dialog;
      setTimeout(function () {
        var live = winHost.querySelector('.w11-dialog');
        if (!live || live.contains(document.activeElement)) return;   // the user is already typing in it
        var f = live.querySelector('input, select'); if (f) f.focus();
      }, 20);
    }
    return box;
  }

  /* ---------------- render */
  function render() {
    var w = gui.win;
    // keep what the user typed in an open dialog when the window re-renders (server responses re-render)
    var keep = {}, focusId = document.activeElement && winHost.contains(document.activeElement) ? document.activeElement.id : null;
    winHost.querySelectorAll('.w11-dialog input, .w11-dialog select').forEach(function (n) { if (n.id) keep[n.id] = n.type === 'checkbox' ? n.checked : n.value; });
    winHost.innerHTML = '';
    document.querySelectorAll('[data-app]').forEach(function (b) { b.classList.toggle('running', b.getAttribute('data-app') === w); });
    if (!w || w === 'start') { winHost.hidden = true; return; }
    var make = { settings: settings, services: services, devmgr: devmgr, ncpa: ncpa, aduc: aduc }[w];
    if (!make) { winHost.hidden = true; return; }
    winHost.hidden = false;
    winHost.appendChild(make());
    Object.keys(keep).forEach(function (id) { var n = document.getElementById(id); if (n) { if (n.type === 'checkbox') n.checked = keep[id]; else n.value = keep[id]; } });
    if (focusId) { var f = document.getElementById(focusId); if (f) f.focus({ preventScroll: true }); }
  }

  /* ---------------- sizing: fit the desk to the visible viewport (portrait + landscape) */
  function size() {
    var vv = window.visualViewport;
    var h = vv ? vv.height : window.innerHeight;
    var top = desk.getBoundingClientRect().top;
    var narrow = desk.clientWidth < 640;
    desk.classList.toggle('narrow', narrow);
    desk.classList.toggle('short', h < 520);
    var want = narrow ? Math.max(420, Math.min(h - 12, 760)) : Math.max(520, Math.min(h - Math.max(top, 0) - 16, 720));
    desk.style.setProperty('--desk-h', want + 'px');
  }
  if (window.ResizeObserver) new ResizeObserver(size).observe(desk);
  window.addEventListener('resize', size);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', size);
  window.addEventListener('orientationchange', function () { setTimeout(size, 250); });
  size();
  filter();
  render();
  window.CIWT_GUI = { send: send, render: render };
})();
