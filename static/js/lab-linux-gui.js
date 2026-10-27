/* Novak LMS™ Live Labs — Ubuntu 24.04 LTS GNOME Desktop Workbench (linuxgui) + Split-Pane Bash Terminal */
(function () {
  'use strict';
  var cfg = window.LabKit && window.LabKit.config();
  if (!cfg) return;
  var kit = window.LabKit.init(cfg);
  var el = window.LabKit.el;
  var winHost = document.getElementById('lnxWinHost');
  var statusStrip = document.getElementById('lnxStatusStrip');
  var activeAppLabel = document.getElementById('lnxActiveAppLabel');
  var trayNet = document.getElementById('lnxTrayNet');
  var grid = document.getElementById('lnxWorkbenchGrid');
  var deskPane = document.getElementById('lnxDesk');
  var termPane = document.getElementById('termWrap');
  if (!winHost) return;

  var gui = (cfg.boot && cfg.boot.linuxgui) || {
    win: 'network',
    net: { iface: 'eth0', connected: true, method: 'dhcp', ipv4: '10.20.40.120', prefix: '24', gateway: '10.20.40.1', dns: '10.20.40.10', applied: false },
    disks: { selected_disk: '/dev/nvme0n1', smart_checked: false, smart_status: 'PASSED (34°C)', sdb1_mounted: false, sdb1_mountpoint: '/srv/data', fstab_opts: 'defaults,noatime,nofail' },
    firewall: { ufw_enabled: false, default_incoming: 'deny', default_outgoing: 'allow', rules: [], services: {} },
    users: { selected_user: 'tech1', accounts: {}, files: {} }
  };

  function send(ev, data) {
    return kit.post(cfg.urls.event, { ev: ev, data: data || {} }).then(function (p) {
      var r = (p && p.result) || {};
      if (r.error) {
        if (statusStrip) statusStrip.textContent = '⚠ ' + r.error;
        kit.toast(r.error, 'error');
      } else if (r.ok) {
        if (statusStrip) statusStrip.textContent = '✓ ' + r.ok;
        kit.say(r.ok);
      }
      if (p && p.linuxgui) gui = p.linuxgui;
      kit.apply(p);
      render();
      return p;
    });
  }

  kit.on(function (p) {
    if (p && p.linuxgui) {
      gui = p.linuxgui;
      render();
    }
  });

  document.querySelectorAll('[data-lnx-app]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      send('open:' + btn.getAttribute('data-lnx-app'));
    });
  });

  document.querySelectorAll('[data-lnx-mode]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var mode = btn.getAttribute('data-lnx-mode');
      document.querySelectorAll('[data-lnx-mode]').forEach(function (b) {
        b.classList.toggle('active', b === btn);
      });
      if (grid) grid.setAttribute('data-mode', mode);
      if (deskPane) deskPane.hidden = mode === 'term';
      if (termPane) termPane.hidden = mode === 'gui';
    });
  });

  function renderNetwork() {
    var net = gui.net || {};
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-secondary">' +
        '<div><h3 class="h6 mb-0 text-info"><i class="bi bi-hdd-network me-1"></i>GNOME Settings → Network (nm-connection-editor)</h3>' +
        '<div class="small text-secondary">Interface: <code>' + (net.iface || 'eth0') + '</code> · State: <span class="badge ' + (net.connected ? 'text-bg-success' : 'text-bg-secondary') + '">' + (net.connected ? 'Connected (1000 Mb/s)' : 'Disconnected') + '</span></div></div>' +
        '<button type="button" class="btn btn-sm btn-outline-light" id="lnxNetToggleBtn">' + (net.connected ? 'Disconnect eth0' : 'Connect eth0') + '</button>' +
      '</div>' +
      '<div class="row g-2 mb-2">' +
        '<div class="col-12 col-sm-4"><label class="form-label small mb-1 text-light">IPv4 Method</label>' +
          '<select id="lnxNetMethod" class="form-select form-select-sm bg-dark text-light border-secondary">' +
            '<option value="dhcp"' + (net.method === 'dhcp' ? ' selected' : '') + '>Automatic (DHCP)</option>' +
            '<option value="manual"' + (net.method === 'manual' ? ' selected' : '') + '>Manual (Static IPv4)</option>' +
          '</select></div>' +
        '<div class="col-8 col-sm-5"><label class="form-label small mb-1 text-light">IPv4 Address</label>' +
          '<input id="lnxNetIp" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (net.ipv4 || '10.20.40.15') + '"></div>' +
        '<div class="col-4 col-sm-3"><label class="form-label small mb-1 text-light">Prefix (CIDR)</label>' +
          '<input id="lnxNetPrefix" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (net.prefix || '24') + '"></div>' +
        '<div class="col-12 col-sm-6"><label class="form-label small mb-1 text-light">Default Gateway</label>' +
          '<input id="lnxNetGw" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (net.gateway || '10.20.40.1') + '"></div>' +
        '<div class="col-12 col-sm-6"><label class="form-label small mb-1 text-light">DNS Servers</label>' +
          '<input id="lnxNetDns" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (net.dns || '10.20.40.10') + '"></div>' +
      '</div>' +
      '<div class="d-flex flex-wrap gap-2 mt-3">' +
        '<button type="button" class="btn btn-sm btn-brand" id="lnxNetSaveBtn"><i class="bi bi-check2 me-1"></i>Save IPv4 Profile</button>' +
        '<button type="button" class="btn btn-sm btn-outline-info" id="lnxNetApplyBtn"><i class="bi bi-arrow-repeat me-1"></i>Apply &amp; Reconnect eth0</button>' +
      '</div>';

    setTimeout(function () {
      var tBtn = document.getElementById('lnxNetToggleBtn');
      if (tBtn) tBtn.onclick = function () { send('net:toggle'); };
      var sBtn = document.getElementById('lnxNetSaveBtn');
      if (sBtn) sBtn.onclick = function () {
        send('net:save_manual', {
          method: (document.getElementById('lnxNetMethod') || {}).value || 'manual',
          ipv4: (document.getElementById('lnxNetIp') || {}).value || '10.20.40.15',
          prefix: (document.getElementById('lnxNetPrefix') || {}).value || '24',
          gateway: (document.getElementById('lnxNetGw') || {}).value || '10.20.40.1',
          dns: (document.getElementById('lnxNetDns') || {}).value || '10.20.40.10'
        });
      };
      var aBtn = document.getElementById('lnxNetApplyBtn');
      if (aBtn) aBtn.onclick = function () { send('net:apply'); };
    }, 0);
    return wrap;
  }

  function renderDisks() {
    var d = gui.disks || {};
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0 text-warning"><i class="bi bi-device-hdd me-1"></i>GNOME Disks &amp; GParted Partition Manager (gnome-disks)</h3>' +
        '<div class="small text-secondary">Block Devices: <code>/dev/nvme0n1</code> (512 GB Primary NVMe) · <code>/dev/sdb</code> (100 GB Data Volume)</div>' +
      '</div>' +
      '<div class="p-2 rounded mb-2" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="d-flex justify-content-between align-items-center flex-wrap gap-2">' +
          '<div><strong>/dev/nvme0n1 — Samsung PM9A1 NVMe (GPT)</strong><div class="small text-secondary">p1: 260 MB FAT32 EFI (<code>/boot/efi</code>) · p2: 511 GB ext4 Root (<code>/</code>)</div></div>' +
          '<button type="button" class="btn btn-sm btn-warning" id="lnxSmartBtn"><i class="bi bi-activity me-1"></i>Run SMART Self-Test</button>' +
        '</div>' +
        '<div class="small mt-1 ' + (d.smart_checked ? 'text-success fw-semibold' : 'text-secondary') + '">SMART Status: ' + (d.smart_checked ? d.smart_status : 'Click Run SMART Self-Test to inspect NVMe health') + '</div>' +
      '</div>' +
      '<div class="p-2 rounded" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">/dev/sdb1 — 100 GB Linux Filesystem (ext4) · Status: <span class="badge ' + (d.sdb1_mounted ? 'text-bg-success' : 'text-bg-secondary') + '">' + (d.sdb1_mounted ? 'Mounted at ' + d.sdb1_mountpoint : 'Unmounted') + '</span></div>' +
        '<div class="row g-2 align-items-end">' +
          '<div class="col-12 col-sm-5"><label class="form-label small mb-1 text-light">Mount Point</label>' +
            '<input id="lnxMountPoint" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (d.sdb1_mountpoint || '/srv/data') + '"></div>' +
          '<div class="col-12 col-sm-7"><label class="form-label small mb-1 text-light">/etc/fstab Mount Options</label>' +
            '<input id="lnxFstabOpts" type="text" class="form-control form-control-sm bg-dark text-light border-secondary" value="' + (d.fstab_opts || 'defaults,noatime,nofail') + '"></div>' +
        '</div>' +
        '<div class="d-flex flex-wrap gap-2 mt-2">' +
          '<button type="button" class="btn btn-sm btn-brand" id="lnxMountBtn"><i class="bi bi-play-fill me-1"></i>Mount /dev/sdb1 &amp; Save /etc/fstab</button>' +
          (d.sdb1_mounted ? '<button type="button" class="btn btn-sm btn-outline-light" id="lnxUnmountBtn">Unmount /dev/sdb1</button>' : '') +
        '</div>' +
      '</div>';

    setTimeout(function () {
      var sb = document.getElementById('lnxSmartBtn');
      if (sb) sb.onclick = function () { send('disks:smart'); };
      var mb = document.getElementById('lnxMountBtn');
      if (mb) mb.onclick = function () {
        send('disks:mount_sdb1', {
          mountpoint: (document.getElementById('lnxMountPoint') || {}).value || '/srv/data',
          fstab_opts: (document.getElementById('lnxFstabOpts') || {}).value || 'defaults,noatime,nofail'
        });
      };
      var ub = document.getElementById('lnxUnmountBtn');
      if (ub) ub.onclick = function () { send('disks:unmount_sdb1'); };
    }, 0);
    return wrap;
  }

  function renderFirewall() {
    var fw = gui.firewall || {};
    var rules = fw.rules || [];
    var svcs = fw.services || {};
    var wrap = el('div', { class: 'lnx-pane' });
    var rulesHtml = rules.map(function (r) {
      return '<tr>' +
        '<td><code>' + r.port + '</code></td>' +
        '<td>' + r.service + '</td>' +
        '<td><span class="badge ' + (r.enabled ? 'text-bg-success' : 'text-bg-secondary') + '">' + (r.enabled ? r.action : 'DISABLED') + '</span></td>' +
        '<td><button type="button" class="btn btn-sm btn-outline-info py-0" data-fw-rule="' + r.port + '">' + (r.enabled ? 'Disable' : 'Enable Rule') + '</button></td>' +
      '</tr>';
    }).join('');

    var svcHtml = Object.keys(svcs).map(function (k) {
      var s = svcs[k];
      var running = (s.state || '').indexOf('running') >= 0;
      return '<div class="d-flex justify-content-between align-items-center py-1 border-bottom border-secondary">' +
        '<div class="small"><code>' + s.unit + '</code> — <span class="' + (running ? 'text-success' : 'text-danger') + '">' + s.state + '</span></div>' +
        '<button type="button" class="btn btn-sm btn-outline-light py-0" data-svc-restart="' + k + '">Start / Restart</button>' +
      '</div>';
    }).join('');

    wrap.innerHTML =
      '<div class="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-secondary flex-wrap gap-2">' +
        '<div><h3 class="h6 mb-0 text-success"><i class="bi bi-shield-lock me-1"></i>GUFW Firewall Configuration &amp; Systemd Services</h3>' +
        '<div class="small text-secondary">Default Policy: Incoming <code>DENY</code> · Outgoing <code>ALLOW</code></div></div>' +
        '<div class="d-flex gap-2">' +
          '<button type="button" class="btn btn-sm ' + (fw.ufw_enabled ? 'btn-success' : 'btn-brand') + '" id="lnxUfwEnableBtn">' +
            (fw.ufw_enabled ? '✓ UFW Enabled' : 'Enable UFW Firewall') +
          '</button>' +
          '<button type="button" class="btn btn-sm btn-outline-info" id="lnxAllowSshHttpsBtn">Allow 22/tcp &amp; 443/tcp</button>' +
        '</div>' +
      '</div>' +
      '<div class="table-responsive mb-2"><table class="table table-sm table-dark mb-0 small"><thead><tr><th>Port</th><th>Service</th><th>State</th><th>Action</th></tr></thead><tbody>' + rulesHtml + '</tbody></table></div>' +
      '<div class="mt-2"><div class="small fw-bold text-info mb-1">Systemd Daemons (systemctl)</div>' + svcHtml + '</div>';

    setTimeout(function () {
      var eb = document.getElementById('lnxUfwEnableBtn');
      if (eb) eb.onclick = function () { send('fw:enable'); };
      var ab = document.getElementById('lnxAllowSshHttpsBtn');
      if (ab) ab.onclick = function () { send('fw:allow_ssh_https'); };
      wrap.querySelectorAll('[data-fw-rule]').forEach(function (b) {
        b.onclick = function () { send('fw:rule:' + b.getAttribute('data-fw-rule')); };
      });
      wrap.querySelectorAll('[data-svc-restart]').forEach(function (b) {
        b.onclick = function () { send('svc:restart:' + b.getAttribute('data-svc-restart')); };
      });
    }, 0);
    return wrap;
  }

  function renderUsersAndFiles() {
    var u = gui.users || {};
    var accs = u.accounts || {};
    var tech1 = accs.tech1 || { full_name: 'Jordan Vance (Tier-1 Tech)', locked: true, sudo: false, groups: ['tech1'] };
    var files = u.files || {};
    var bsh = files['/home/trainee/support/backup.sh'] || { mode: '644', exec_bit: false };

    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0" style="color:#a78bfa"><i class="bi bi-people me-1"></i>GNOME Users &amp; Nautilus File Permissions</h3>' +
        '<div class="small text-secondary">Manage local accounts, <code>sudo</code> administrator group membership, and POSIX file permission bits.</div>' +
      '</div>' +
      '<div class="p-2 rounded mb-2" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">User Account: <code>tech1</code> — ' + tech1.full_name + '</div>' +
        '<div class="small mb-2">Status: <span class="badge ' + (tech1.locked ? 'text-bg-danger' : 'text-bg-success') + '">' + (tech1.locked ? 'Locked Out' : 'Unlocked (Active)') + '</span> · ' +
          'Role: <span class="badge ' + (tech1.sudo ? 'text-bg-info' : 'text-bg-secondary') + '">' + (tech1.sudo ? 'Administrator (sudo)' : 'Standard User') + '</span> · ' +
          'Groups: <code>' + (tech1.groups || []).join(', ') + '</code></div>' +
        '<div class="d-flex flex-wrap gap-2">' +
          '<button type="button" class="btn btn-sm btn-brand" id="lnxUnlockTech1Btn"><i class="bi bi-unlock me-1"></i>Unlock Account (tech1)</button>' +
          '<button type="button" class="btn btn-sm btn-outline-info" id="lnxSudoTech1Btn"><i class="bi bi-shield-plus me-1"></i>Grant Administrator (sudo)</button>' +
        '</div>' +
      '</div>' +
      '<div class="p-2 rounded" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1"><i class="bi bi-folder2-open me-1"></i>Nautilus Properties → Permissions: <code>/home/trainee/support/backup.sh</code></div>' +
        '<div class="small mb-2">Current Mode: <code>' + bsh.mode + '</code> · Allow executing file as program: <strong>' + (bsh.exec_bit ? 'ON (+x)' : 'OFF') + '</strong></div>' +
        '<div class="d-flex flex-wrap gap-2">' +
          '<button type="button" class="btn btn-sm btn-brand" id="lnxChmod750Btn"><i class="bi bi-file-earmark-code me-1"></i>Apply Mode 750 (rwxr-x--- + Executable)</button>' +
          '<button type="button" class="btn btn-sm btn-outline-light" id="lnxChmod640Btn">Apply Mode 640 (rw-r-----)</button>' +
        '</div>' +
      '</div>';

    setTimeout(function () {
      var uBtn = document.getElementById('lnxUnlockTech1Btn');
      if (uBtn) uBtn.onclick = function () { send('users:unlock:tech1'); };
      var sBtn = document.getElementById('lnxSudoTech1Btn');
      if (sBtn) sBtn.onclick = function () { send('users:sudo:tech1'); };
      var c750 = document.getElementById('lnxChmod750Btn');
      if (c750) c750.onclick = function () { send('files:chmod:backup.sh:750'); };
      var c640 = document.getElementById('lnxChmod640Btn');
      if (c640) c640.onclick = function () { send('files:chmod:backup.sh:640'); };
    }, 0);
    return wrap;
  }

  function render() {
    var w = (gui && gui.win) || 'network';
    document.querySelectorAll('[data-lnx-app]').forEach(function (b) {
      var active = b.getAttribute('data-lnx-app') === w;
      b.style.boxShadow = active ? '0 0 0 2px #f8fafc' : 'none';
    });
    if (activeAppLabel) {
      var names = {
        network: 'GNOME Settings — Network',
        disks: 'GNOME Disks & GParted',
        firewall: 'GUFW Firewall & Systemd',
        users: 'GNOME Users & Sudo',
        files: 'Nautilus Files & Permissions'
      };
      activeAppLabel.textContent = names[w] || 'GNOME Settings';
    }
    if (trayNet && gui.net) {
      trayNet.textContent = gui.net.connected ? (gui.net.ipv4 || '10.20.40.15') : 'Offline';
    }
    winHost.innerHTML = '';
    if (w === 'disks') winHost.appendChild(renderDisks());
    else if (w === 'firewall') winHost.appendChild(renderFirewall());
    else if (w === 'users' || w === 'files') winHost.appendChild(renderUsersAndFiles());
    else winHost.appendChild(renderNetwork());
  }

  render();
  window.NOVAK_LINUX_GUI = { send: send, render: render };
})();
