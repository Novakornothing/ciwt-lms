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

  var defaultWinByLab = {
    'linux-gui-network': 'network',
    'linux-gui-disks': 'disks',
    'linux-gui-firewall': 'firewall',
    'linux-gui-users': 'users',
    'linux-gui-logs': 'logs',
    'linux-gui-processes': 'processes',
    'linux-gui-packages': 'packages',
    'linux-gui-ssh': 'ssh'
  };

  var gui = (cfg.boot && cfg.boot.linuxgui) || {
    win: defaultWinByLab[cfg.lab_id] || 'network',
    net: { iface: 'eth0', connected: true, method: 'dhcp', ipv4: '10.20.40.120', prefix: '24', gateway: '10.20.40.1', dns: '10.20.40.10', applied: false },
    disks: { selected_disk: '/dev/nvme0n1', smart_checked: false, smart_status: 'PASSED (34°C)', sdb1_mounted: false, sdb1_mountpoint: '/srv/data', fstab_opts: 'defaults,noatime,nofail' },
    firewall: { ufw_enabled: false, default_incoming: 'deny', default_outgoing: 'allow', rules: [], services: {} },
    users: { selected_user: 'tech1', accounts: {}, files: {} },
    logs: { unit_filter: 'all', severity_filter: 'all', filtered_ssh: false, banned_ip: null, journal_usage_mb: 640, vacuumed: false },
    processes: { runaway_pid: 4412, runaway_name: 'stress-ng-worker', runaway_cpu: 98.4, runaway_nice: 0, runaway_state: 'R (running)', killed: false, swappiness: 60, swappiness_tuned: false },
    packages: { apt_updated: false, last_update: '42 days ago (stale cache)', unattended_installed: false, cron_schedule: '0 2 * * * /usr/local/bin/backup-verify.sh', cron_enabled: false },
    ssh: { ed25519_generated: false, ed25519_fp: 'SHA256:9xK4mP8vR2nL7qW3cT6yB1zF5jH0dG8sA4eU2iO6pY', permit_root_login: 'yes', password_auth: 'yes', hardened: false, sshd_reloaded: false }
  };

  if (cfg.lab_id && defaultWinByLab[cfg.lab_id] && (!cfg.boot || !cfg.boot.linuxgui || !cfg.boot.linuxgui.log || !cfg.boot.linuxgui.log.length)) {
    gui.win = defaultWinByLab[cfg.lab_id];
  }

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

  function renderLogs() {
    var lg = gui.logs || { unit_filter: 'all', severity_filter: 'all', filtered_ssh: false, banned_ip: null, journal_usage_mb: 640, vacuumed: false };
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0 text-danger"><i class="bi bi-journal-code me-1"></i>GNOME Logs — systemd-journald &amp; Security Audit (gnome-logs)</h3>' +
        '<div class="small text-secondary">Filter: Unit=<code>' + lg.unit_filter + '</code> · Priority=<code>' + lg.severity_filter + '</code> · Archive Size: <code>' + lg.journal_usage_mb + ' MB</code></div>' +
      '</div>' +
      '<div class="d-flex flex-wrap gap-2 mb-2">' +
        '<button type="button" class="btn btn-sm btn-brand" id="lnxFilterSshBtn"><i class="bi bi-funnel me-1"></i>Filter ssh.service Errors (journalctl -u ssh -p err)</button>' +
        '<button type="button" class="btn btn-sm btn-danger" id="lnxBanIpBtn"><i class="bi bi-shield-slash me-1"></i>' + (lg.banned_ip ? '✓ Blocked ' + lg.banned_ip : 'Block Attacker IP 198.51.100.77 (UFW / Fail2Ban)') + '</button>' +
        '<button type="button" class="btn btn-sm btn-outline-warning" id="lnxVacuumBtn"><i class="bi bi-trash3 me-1"></i>' + (lg.vacuumed ? '✓ Vacuumed to 92 MB' : 'Vacuum Journal to 100 MB') + '</button>' +
      '</div>' +
      '<pre class="p-2 rounded small mb-0 font-monospace" style="background:#090d16;color:#e2e8f0;border:1px solid rgba(248,113,113,0.3);max-height:210px;overflow-y:auto">' +
        (lg.filtered_ssh
          ? 'Oct 27 09:38:11 novak-lnx-01 sshd[3902]: error: PAM: Authentication failure for root from 198.51.100.77 port 51924 ssh2\n' +
            'Oct 27 09:38:14 novak-lnx-01 sshd[3908]: Failed password for invalid user admin from 198.51.100.77 port 51988 ssh2\n' +
            'Oct 27 09:38:19 novak-lnx-01 sshd[3915]: error: maximum authentication attempts exceeded for root from 198.51.100.77 port 52010 ssh2 [preauth]\n' +
            (lg.banned_ip ? 'Oct 27 09:41:02 novak-lnx-01 fail2ban.actions[1120]: NOTICE [sshd] Ban 198.51.100.77 via ufw\n' : '')
          : 'Oct 27 09:35:01 novak-lnx-01 systemd[1]: Started Run anacron jobs.\n' +
            'Oct 27 09:38:11 novak-lnx-01 sshd[3902]: error: PAM: Authentication failure for root from 198.51.100.77 port 51924 ssh2\n' +
            'Oct 27 09:39:00 novak-lnx-01 NetworkManager[814]: <info>  [1793064000] manager: NetworkManager state is now CONNECTED_GLOBAL\n' +
            'Click "Filter ssh.service Errors" above to isolate security authentication failures.') +
      '</pre>';

    setTimeout(function () {
      var fb = document.getElementById('lnxFilterSshBtn');
      if (fb) fb.onclick = function () { send('logs:filter_ssh'); };
      var bb = document.getElementById('lnxBanIpBtn');
      if (bb) bb.onclick = function () { send('logs:ban:198.51.100.77'); };
      var vb = document.getElementById('lnxVacuumBtn');
      if (vb) vb.onclick = function () { send('logs:vacuum'); };
    }, 0);
    return wrap;
  }

  function renderProcesses() {
    var pr = gui.processes || { runaway_pid: 4412, runaway_name: 'stress-ng-worker', runaway_cpu: 98.4, runaway_nice: 0, runaway_state: 'R (running)', killed: false, swappiness: 60, swappiness_tuned: false };
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0 text-info"><i class="bi bi-cpu me-1"></i>GNOME System Monitor — Processes, CPU &amp; Memory Pressure</h3>' +
        '<div class="small text-secondary">CPU Load: <strong class="' + (pr.killed ? 'text-success' : 'text-danger') + '">' + (pr.killed ? '4.2% (Normal)' : '98.4% (Pegged by PID 4412)') + '</strong> · Kernel <code>vm.swappiness</code>: <code>' + pr.swappiness + '</code></div>' +
      '</div>' +
      '<div class="table-responsive mb-2"><table class="table table-sm table-dark mb-0 small"><thead><tr><th>PID</th><th>Process</th><th>User</th><th>%CPU</th><th>Nice</th><th>State</th><th>Action</th></tr></thead><tbody>' +
        '<tr><td><code>4412</code></td><td><strong>' + pr.runaway_name + '</strong></td><td>trainee</td><td><span class="badge ' + (pr.killed ? 'text-bg-secondary' : 'text-bg-danger') + '">' + pr.runaway_cpu + '%</span></td><td>' + pr.runaway_nice + '</td><td>' + pr.runaway_state + '</td>' +
          '<td><button type="button" class="btn btn-sm btn-danger py-0" id="lnxKillPidBtn"' + (pr.killed ? ' disabled' : '') + '>' + (pr.killed ? 'Terminated' : 'Terminate PID 4412') + '</button></td></tr>' +
        '<tr><td><code>1042</code></td><td>nginx: master</td><td>root</td><td>0.4%</td><td>0</td><td>S (sleeping)</td><td><span class="text-secondary small">Healthy</span></td></tr>' +
        '<tr><td><code>814</code></td><td>NetworkManager</td><td>root</td><td>0.3%</td><td>0</td><td>S (sleeping)</td><td><span class="text-secondary small">Healthy</span></td></tr>' +
      '</tbody></table></div>' +
      '<div class="p-2 rounded d-flex justify-content-between align-items-center flex-wrap gap-2" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="small"><strong>Kernel Swap Pressure (<code>vm.swappiness</code>):</strong> Current = <code>' + pr.swappiness + '</code> (Default 60 swaps aggressively; workstation target is <code>10</code>)</div>' +
        '<button type="button" class="btn btn-sm btn-brand" id="lnxSwappinessBtn"><i class="bi bi-sliders me-1"></i>' + (pr.swappiness_tuned ? '✓ vm.swappiness=10 Applied' : 'Apply vm.swappiness=10') + '</button>' +
      '</div>';

    setTimeout(function () {
      var kb = document.getElementById('lnxKillPidBtn');
      if (kb) kb.onclick = function () { send('proc:kill:4412'); };
      var sb = document.getElementById('lnxSwappinessBtn');
      if (sb) sb.onclick = function () { send('proc:swappiness:10'); };
    }, 0);
    return wrap;
  }

  function renderPackages() {
    var pk = gui.packages || { apt_updated: false, last_update: '42 days ago (stale cache)', unattended_installed: false, cron_schedule: '0 2 * * * /usr/local/bin/backup-verify.sh', cron_enabled: false };
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0 text-warning"><i class="bi bi-box-seam me-1"></i>Ubuntu Software &amp; Updates (APT) + Cron Task Scheduler</h3>' +
        '<div class="small text-secondary">APT Repository Cache: <code>' + pk.last_update + '</code></div>' +
      '</div>' +
      '<div class="p-2 rounded mb-2" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">1. APT Package Lists &amp; Unattended Security Upgrades</div>' +
        '<div class="small mb-2">Status: <span class="badge ' + (pk.apt_updated ? 'text-bg-success' : 'text-bg-warning') + '">' + (pk.apt_updated ? 'APT Synced' : 'Stale Cache') + '</span> · ' +
          '<code>unattended-upgrades</code>: <span class="badge ' + (pk.unattended_installed ? 'text-bg-success' : 'text-bg-secondary') + '">' + (pk.unattended_installed ? 'Installed &amp; Active' : 'Not Installed') + '</span></div>' +
        '<div class="d-flex flex-wrap gap-2">' +
          '<button type="button" class="btn btn-sm btn-brand" id="lnxAptUpdateBtn"><i class="bi bi-arrow-repeat me-1"></i>Refresh APT Cache (apt update)</button>' +
          '<button type="button" class="btn btn-sm btn-outline-info" id="lnxInstallUnattendedBtn"><i class="bi bi-shield-check me-1"></i>Install unattended-upgrades</button>' +
        '</div>' +
      '</div>' +
      '<div class="p-2 rounded" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">2. Scheduled Maintenance (<code>/etc/crontab</code> &amp; <code>cron.service</code>)</div>' +
        '<div class="small mb-2">Job: <code>' + pk.cron_schedule + '</code> · State: <span class="badge ' + (pk.cron_enabled ? 'text-bg-success' : 'text-bg-secondary') + '">' + (pk.cron_enabled ? 'Enabled (02:00 Daily)' : 'Disabled (Commented Out)') + '</span></div>' +
        '<button type="button" class="btn btn-sm btn-brand" id="lnxCronEnableBtn"><i class="bi bi-clock-history me-1"></i>Enable Nightly Cron Job (0 2 * * *)</button>' +
      '</div>';

    setTimeout(function () {
      var ab = document.getElementById('lnxAptUpdateBtn');
      if (ab) ab.onclick = function () { send('pkg:apt_update'); };
      var ib = document.getElementById('lnxInstallUnattendedBtn');
      if (ib) ib.onclick = function () { send('pkg:install:unattended-upgrades'); };
      var cb = document.getElementById('lnxCronEnableBtn');
      if (cb) cb.onclick = function () { send('pkg:cron_enable'); };
    }, 0);
    return wrap;
  }

  function renderSsh() {
    var sh = gui.ssh || { ed25519_generated: false, ed25519_fp: 'SHA256:9xK4mP8vR2nL7qW3cT6yB1zF5jH0dG8sA4eU2iO6pY', permit_root_login: 'yes', password_auth: 'yes', hardened: false, sshd_reloaded: false };
    var wrap = el('div', { class: 'lnx-pane' });
    wrap.innerHTML =
      '<div class="mb-2 pb-2 border-bottom border-secondary">' +
        '<h3 class="h6 mb-0" style="color:#f472b6"><i class="bi bi-key me-1"></i>GNOME Passwords &amp; Keys (Seahorse) + OpenSSH Hardening</h3>' +
        '<div class="small text-secondary">Keyring: <code>~/.ssh/id_ed25519</code> · Daemon Config: <code>/etc/ssh/sshd_config</code></div>' +
      '</div>' +
      '<div class="p-2 rounded mb-2" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">1. OpenSSH Ed25519 Keypair (<code>ssh-keygen -t ed25519</code>)</div>' +
        '<div class="small mb-2">' + (sh.ed25519_generated ? '<span class="text-success">✓ Keypair Active: <code>' + sh.ed25519_fp + '</code></span>' : 'No Ed25519 keypair in <code>~/.ssh</code> yet.') + '</div>' +
        '<button type="button" class="btn btn-sm btn-brand" id="lnxKeygenBtn"><i class="bi bi-key-fill me-1"></i>Generate Ed25519 Keypair &amp; Authorize</button>' +
      '</div>' +
      '<div class="p-2 rounded" style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.12)">' +
        '<div class="fw-bold mb-1">2. OpenSSH Server Security Policy (<code>/etc/ssh/sshd_config</code>)</div>' +
        '<div class="small mb-2"><code>PermitRootLogin</code>: <span class="badge ' + (sh.permit_root_login === 'no' ? 'text-bg-success' : 'text-bg-danger') + '">' + sh.permit_root_login + '</span> · ' +
          '<code>PasswordAuthentication</code>: <span class="badge ' + (sh.password_auth === 'no' ? 'text-bg-success' : 'text-bg-danger') + '">' + sh.password_auth + '</span> · ' +
          '<code>ssh.service</code>: <span class="badge ' + (sh.sshd_reloaded ? 'text-bg-success' : 'text-bg-secondary') + '">' + (sh.sshd_reloaded ? 'Reloaded &amp; Verified' : 'Pending Reload') + '</span></div>' +
        '<div class="d-flex flex-wrap gap-2">' +
          '<button type="button" class="btn btn-sm btn-brand" id="lnxHardenSshBtn"><i class="bi bi-lock-fill me-1"></i>Apply Hardened sshd_config (Disable Root &amp; Password Auth)</button>' +
          '<button type="button" class="btn btn-sm btn-outline-info" id="lnxReloadSshBtn"><i class="bi bi-arrow-repeat me-1"></i>Validate sshd -t &amp; Reload ssh.service</button>' +
        '</div>' +
      '</div>';

    setTimeout(function () {
      var kb = document.getElementById('lnxKeygenBtn');
      if (kb) kb.onclick = function () { send('ssh:keygen'); };
      var hb = document.getElementById('lnxHardenSshBtn');
      if (hb) hb.onclick = function () { send('ssh:harden'); };
      var rb = document.getElementById('lnxReloadSshBtn');
      if (rb) rb.onclick = function () { send('ssh:reload'); };
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
        users: 'GNOME Users & Nautilus Permissions',
        files: 'Nautilus Files & Permissions',
        logs: 'GNOME Logs (journalctl)',
        processes: 'GNOME System Monitor',
        packages: 'Ubuntu Software & Cron',
        ssh: 'Passwords & SSH Keys (Seahorse)'
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
    else if (w === 'logs') winHost.appendChild(renderLogs());
    else if (w === 'processes') winHost.appendChild(renderProcesses());
    else if (w === 'packages') winHost.appendChild(renderPackages());
    else if (w === 'ssh') winHost.appendChild(renderSsh());
    else winHost.appendChild(renderNetwork());
  }

  render();
  window.NOVAK_LINUX_GUI = { send: send, render: render };
})();
