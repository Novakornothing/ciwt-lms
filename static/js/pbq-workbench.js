/* ==========================================================================
   Novak LMS™ — Interactive Visual PBQ Workbench (Pearson VUE / TestOut Style)
   Provides context-aware interactive SVG diagrams (Network Topology, Hardware
   Bay, System & Security Architecture), Live Device Inspector / Telemetry Feed,
   Interactive Diagnostic Terminal (pbq-cli), and bidirectional DOM row sync.
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.PBQWorkbench = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var TAB_NAMES = [
    { id: 'visualizer', label: 'Topology & Hardware Visualizer' },
    { id: 'inspector', label: 'Live Device Inspector / Logs' },
    { id: 'terminal', label: 'Diagnostic Terminal' }
  ];

  var DEFAULT_CLI_PILLS = [
    'help',
    'status',
    'show run',
    'show vlan',
    'show ip route',
    'ping',
    'nslookup',
    'ipconfig /all',
    'diskpart',
    'bootrec',
    'permissions',
    'inspect 1'
  ];

  function escHtml(str) {
    return String(str == null ? '' : str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function truncate(str, maxLen) {
    var s = String(str == null ? '' : str).trim();
    if (!s) return '';
    return s.length > maxLen ? s.slice(0, maxLen - 1) + '…' : s;
  }

  /**
   * Detects the optimal visual workbench mode ('network' | 'hardware' | 'system')
   * from the PBQ metadata (examCode, lo, text, prompts, nodes, commands).
   */
  function detectWorkbenchMode(meta) {
    meta = meta || {};
    var examCode = String(meta.examCode || '').toUpperCase();
    var lo = String(meta.lo || '').toUpperCase();
    var corpus = [
      meta.text || '',
      meta.lo || '',
      meta.loTitle || '',
      (meta.prompts || []).join(' '),
      (meta.nodes || []).map(function (n) { return (n.name || n[0] || '') + ' ' + (n.detail || n[1] || ''); }).join(' '),
      Object.keys(meta.commands || {}).join(' '),
      meta.inspectorText || ''
    ].join(' ').toLowerCase();

    var netScore = 0;
    var hwScore = 0;
    var sysScore = 0;

    var netKeywords = [
      ['vlan', 4], ['ospf', 5], ['trunk', 4], ['switchport', 5], ['802.1q', 5],
      ['access-list', 5], ['acl', 4], ['subnet', 4], ['cidr', 4], ['dhcp', 3],
      ['apipa', 4], ['169.254', 4], ['nslookup', 4], ['wi-fi', 4], ['ssid', 4],
      ['wpa', 4], ['802.11', 4], ['router', 3], ['switch', 3], ['dmz', 4],
      ['radius', 4], ['tacacs', 4], ['wlc', 4], ['nat', 3], ['bgp', 4],
      ['wan', 3], ['pan', 2], ['man', 2], ['captive portal', 4], ['default gateway', 3],
      ['intranet', 3], ['show ip route', 5], ['show interfaces trunk', 5], ['show vlan', 5]
    ];

    var hwKeywords = [
      ['m.2', 5], ['nvme', 5], ['dimm', 5], ['pcie', 5], ['sata', 4],
      ['psu', 5], ['power supply', 4], ['motherboard', 5], ['board diagram', 5],
      ['t568a', 6], ['t568b', 6], ['pinout', 6], ['wiremap', 6], ['patch cable', 5],
      ['rj-45', 5], ['crimper', 5], ['laser', 5], ['printer', 4], ['fuser', 5],
      ['toner', 5], ['maintenance kit', 5], ['raid', 4], ['replacing a desktop', 5],
      ['laptop keyboard', 5], ['ram', 3], ['chassis', 4], ['hypervisor', 3],
      ['pin 1', 4], ['pin 2', 4], ['pin 3', 4], ['pin 6', 4], ['smart', 3], ['post', 2]
    ];

    var sysKeywords = [
      ['icacls', 6], ['ntfs', 6], ['posix', 5], ['chmod', 5], ['permission', 4],
      ['share name', 5], ['net share', 5], ['termservice', 6], ['remote desktop', 5],
      ['netfirewallrule', 5], ['powershell', 4], ['get-service', 5],
      ['malware', 5], ['quarantine', 5], ['system restore', 5], ['searchhelperpro', 6],
      ['task manager', 5], ['tasklist', 5], ['render_preview', 6], ['fsutil', 6],
      ['volume d:', 5], ['diskfree', 5], ['bcdedit', 5], ['bootrec', 5], ['diskpart', 5],
      ['gpt', 4], ['partition', 4], ['gpo', 5], ['group policy', 5], ['sql', 5],
      ['schema', 4], ['database', 3], ['systemd', 5], ['systemctl', 5], ['event viewer', 4],
      ['windows 11', 4], ['linux', 4], ['active directory', 4]
    ];

    netKeywords.forEach(function (kw) { if (corpus.indexOf(kw[0]) !== -1) netScore += kw[1]; });
    hwKeywords.forEach(function (kw) { if (corpus.indexOf(kw[0]) !== -1) hwScore += kw[1]; });
    sysKeywords.forEach(function (kw) { if (corpus.indexOf(kw[0]) !== -1) sysScore += kw[1]; });

    // Exam code baseline tie-breakers
    if (examCode.indexOf('N10-009') !== -1 || lo.indexOf('N10-009') !== -1 || /^N:/i.test(lo)) {
      netScore += 3;
    } else if (examCode.indexOf('220-1201') !== -1 || lo.indexOf('220-1201') !== -1 || /^A1:/i.test(lo)) {
      hwScore += 3;
    } else if (
      examCode.indexOf('220-1202') !== -1 || lo.indexOf('220-1202') !== -1 || /^A2:/i.test(lo) ||
      examCode.indexOf('FC0-U71') !== -1 || lo.indexOf('FC0-U71') !== -1 || /^T:/i.test(lo)
    ) {
      sysScore += 3;
    }

    if (hwScore >= netScore && hwScore >= sysScore && hwScore > 0) return 'hardware';
    if (sysScore >= netScore && sysScore >= hwScore && sysScore > 0) return 'system';
    if (netScore > 0) return 'network';
    return 'network';
  }

  var MODE_TEMPLATES = {
    network: {
      bannerTitle: 'NETWORK TOPOLOGY & PACKET TELEMETRY MATRIX',
      bannerSub: 'Interactive L2/L3 Switching, Routing, Firewall & Wireless Telemetry',
      badgeLabel: 'Network & Security Topology',
      nodes: [
        { id: 'core-router', title: 'Core Router', role: 'L3 Routing / OSPF / GatewaySubinterfaces', x: 30, y: 52, w: 235, h: 98 },
        { id: 'l2-l3-switch', title: 'L2/L3 Switch', role: '802.1Q Trunking & VLAN Access Ports', x: 292, y: 52, w: 235, h: 98 },
        { id: 'firewall-dmz', title: 'Firewall / DMZ', role: 'Stateful ACLs & Perimeter Policy', x: 554, y: 52, w: 235, h: 98 },
        { id: 'radius-dns', title: 'RADIUS / DNS Server', role: 'AAA, DHCP Scopes & Name Resolution', x: 30, y: 178, w: 235, h: 98 },
        { id: 'wlc-aps', title: 'WLC / APs', role: '802.11ax WLANs, WPA3-SAE & Guest Isolation', x: 292, y: 178, w: 235, h: 98 },
        { id: 'branch-subnets', title: 'Branch Subnets', role: 'Endpoint Hosts, VLAN Segments & Gateways', x: 554, y: 178, w: 235, h: 98 }
      ],
      links: [
        [0, 1], [1, 2], [0, 3], [1, 4], [2, 5], [1, 5]
      ]
    },
    hardware: {
      bannerTitle: 'HARDWARE BAY / CHASSIS & PINOUT DIAGNOSTIC BENCH',
      bannerSub: 'Interactive Motherboard Bus, ATX PSU Rails, Imaging & Structured Cabling',
      badgeLabel: 'Hardware & Cabling Bench',
      nodes: [
        { id: 'cpu-pcie-dimm', title: 'CPU/PCIe/DIMM', role: 'PCIe 4.0 Lanes, M.2 NVMe & Dual-Channel RAM', x: 30, y: 52, w: 235, h: 98 },
        { id: 'psu-rails', title: 'PSU Rails', role: 'ATX 24-Pin / EPS +12V, +5V & +3.3V Telemetry', x: 292, y: 52, w: 235, h: 98 },
        { id: 'laser-imaging', title: 'Laser Imaging Assembly', role: 'Imaging Drum, Fuser Unit, Transfer Belt & Rollers', x: 554, y: 52, w: 235, h: 98 },
        { id: 'patch-panel', title: 'RJ-45/Fiber Patch Panel', role: 'T568A/T568B Pinout Termination & TDR Tester', x: 145, y: 178, w: 250, h: 98 },
        { id: 'hypervisor-host', title: 'Hypervisor Host', role: 'RAID Storage Bay, UEFI Boot & Virtualization Host', x: 425, y: 178, w: 250, h: 98 }
      ],
      links: [
        [0, 1], [0, 4], [1, 2], [0, 3], [3, 4]
      ]
    },
    system: {
      bannerTitle: 'SYSTEM, SECURITY & ARCHITECTURE PIPELINE WORKBENCH',
      bannerSub: 'Interactive Boot/Partition Map, Permission Matrix, Daemons & Runtime Trace',
      badgeLabel: 'System & Security Architecture',
      nodes: [
        { id: 'uefi-gpt-map', title: 'UEFI/GPT Partition Map', role: 'EFI System Partition, BCD Store & Volume Free Space', x: 30, y: 52, w: 365, h: 98 },
        { id: 'ntfs-posix-matrix', title: 'NTFS/POSIX Permission Matrix', role: 'Share & NTFS Effective ACLs / POSIX Mode Bits', x: 425, y: 52, w: 365, h: 98 },
        { id: 'service-gpo-pipeline', title: 'Service/GPO Pipeline', role: 'System Services, Host Firewall Rules & Remediation Order', x: 30, y: 178, w: 365, h: 98 },
        { id: 'sql-logic-trace', title: 'SQL Schema / Logic Trace', role: 'Process Telemetry, Startup Impact & Query/Runtime State', x: 425, y: 178, w: 365, h: 98 }
      ],
      links: [
        [0, 1], [0, 2], [1, 3], [2, 3]
      ]
    }
  };

  /**
   * Builds the list of interactive diagram nodes for a PBQ, mapping each node
   * to a configuration prompt row index and enriching with scenario details.
   */
  function buildDiagramNodes(meta) {
    meta = meta || {};
    var mode = meta.mode || detectWorkbenchMode(meta);
    var tpl = MODE_TEMPLATES[mode] || MODE_TEMPLATES.network;
    var prompts = Array.isArray(meta.prompts) && meta.prompts.length ? meta.prompts : ['Task 1', 'Task 2', 'Task 3'];
    var simNodes = Array.isArray(meta.nodes) ? meta.nodes : [];

    var nodes = tpl.nodes.map(function (base, idx) {
      var rowIdx = idx < prompts.length ? idx : (idx % prompts.length);
      var simNode = simNodes[idx] || null;
      var simName = simNode ? (simNode.name || simNode[0] || '') : '';
      var simDetail = simNode ? (simNode.detail || simNode[1] || '') : '';
      var displayTitle = simName ? (base.title + ' (' + simName + ')') : base.title;
      return {
        index: idx,
        id: base.id,
        title: displayTitle,
        canonicalTitle: base.title,
        role: simDetail || base.role,
        rowIndex: rowIdx,
        prompt: prompts[rowIdx] || ('Task ' + (rowIdx + 1)),
        x: base.x,
        y: base.y,
        w: base.w,
        h: base.h
      };
    });

    // If there are more prompt rows than template nodes, ensure every prompt row has a direct node
    if (prompts.length > nodes.length) {
      for (var extra = nodes.length; extra < prompts.length; extra++) {
        var col = extra % 3;
        nodes.push({
          index: extra,
          id: 'stage-' + (extra + 1),
          title: 'Stage ' + (extra + 1) + ': ' + truncate(prompts[extra], 22),
          canonicalTitle: 'Stage ' + (extra + 1),
          role: 'Configuration Task #' + (extra + 1),
          rowIndex: extra,
          prompt: prompts[extra],
          x: 30 + col * 262,
          y: 178,
          w: 235,
          h: 98
        });
      }
    }

    return nodes;
  }

  /**
   * Synthesizes an interactive SVG diagram for the PBQ workbench.
   */
  function renderDiagramSvg(meta, selections, activeNodeIndex) {
    meta = meta || {};
    selections = Array.isArray(selections) ? selections : [];
    var mode = meta.mode || detectWorkbenchMode(meta);
    var tpl = MODE_TEMPLATES[mode] || MODE_TEMPLATES.network;
    var nodes = buildDiagramNodes(meta);
    var activeIdx = typeof activeNodeIndex === 'number' ? activeNodeIndex : 0;

    var parts = [];
    parts.push(
      '<svg class="pbq-wb-svg" viewBox="0 0 820 300" role="img" aria-label="' +
      escHtml(tpl.bannerTitle) + '" data-wb-mode="' + escHtml(mode) + '">'
    );

    // Subtle blueprint grid
    for (var gx = 40; gx < 820; gx += 40) {
      parts.push('<line class="pbq-svg-grid-line" x1="' + gx + '" y1="38" x2="' + gx + '" y2="295" />');
    }
    for (var gy = 60; gy < 300; gy += 40) {
      parts.push('<line class="pbq-svg-grid-line" x1="10" y1="' + gy + '" x2="810" y2="' + gy + '" />');
    }

    // Top blueprint banner
    parts.push('<rect class="pbq-svg-banner" x="10" y="8" width="800" height="28" rx="5" ry="5" />');
    parts.push('<text class="pbq-svg-banner-text" x="22" y="26">' + escHtml(tpl.bannerTitle) + '</text>');
    parts.push('<text class="pbq-svg-banner-sub" x="798" y="26" text-anchor="end">' + escHtml(tpl.badgeLabel) + '</text>');

    // Interconnection links
    tpl.links.forEach(function (pair) {
      var a = nodes[pair[0]];
      var b = nodes[pair[1]];
      if (!a || !b) return;
      var x1 = Math.round(a.x + a.w / 2);
      var y1 = Math.round(a.y + a.h / 2);
      var x2 = Math.round(b.x + b.w / 2);
      var y2 = Math.round(b.y + b.h / 2);
      var bothConfigured = Boolean(selections[a.rowIndex] && selections[b.rowIndex]);
      var linkCls = 'pbq-svg-link' + (bothConfigured ? ' pbq-link-configured' : '');
      parts.push('<line class="' + linkCls + '" x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" />');
    });

    // Interactive SVG nodes
    nodes.forEach(function (n) {
      var chosenVal = String(selections[n.rowIndex] || '').trim();
      var isConfigured = chosenVal.length > 0;
      var isActive = n.index === activeIdx;
      var cls = 'pbq-svg-node' +
        (isActive ? ' is-active' : '') +
        (isConfigured ? ' pbq-node-configured' : '');

      var badgeText = isConfigured
        ? ('✓ ' + truncate(chosenVal, 26))
        : ('Task #' + (n.rowIndex + 1) + ': Unconfigured');

      parts.push(
        '<g class="' + cls + '" role="button" tabindex="0" ' +
        'data-node-index="' + n.index + '" data-row-index="' + n.rowIndex + '" ' +
        'aria-label="' + escHtml(n.title + ' — ' + n.prompt) + '">'
      );
      parts.push('<rect class="pbq-svg-node-box" x="' + n.x + '" y="' + n.y + '" width="' + n.w + '" height="' + n.h + '" />');
      parts.push('<circle class="pbq-svg-led" cx="' + (n.x + 16) + '" cy="' + (n.y + 20) + '" r="5" />');
      parts.push('<text class="pbq-svg-node-title" x="' + (n.x + 28) + '" y="' + (n.y + 24) + '">' + escHtml(truncate(n.title, 30)) + '</text>');
      parts.push('<text class="pbq-svg-node-sub" x="' + (n.x + 14) + '" y="' + (n.y + 44) + '">' + escHtml(truncate(n.role, 38)) + '</text>');
      parts.push('<text class="pbq-svg-node-sub" x="' + (n.x + 14) + '" y="' + (n.y + 60) + '">Row ' + (n.rowIndex + 1) + ': ' + escHtml(truncate(n.prompt, 32)) + '</text>');
      parts.push('<rect class="pbq-svg-badge-bg" x="' + (n.x + 12) + '" y="' + (n.y + 68) + '" width="' + (n.w - 24) + '" height="22" />');
      parts.push('<text class="pbq-svg-badge-text" x="' + (n.x + 20) + '" y="' + (n.y + 83) + '">' + escHtml(badgeText) + '</text>');
      parts.push('</g>');
    });

    parts.push('</svg>');
    return parts.join('');
  }

  /**
   * Synthesizes realistic, contextual diagnostic telemetry for Tab 2 (Live Device Inspector).
   */
  function buildInspectorTelemetry(meta, nodeIndex, selections) {
    meta = meta || {};
    selections = Array.isArray(selections) ? selections : [];
    var mode = meta.mode || detectWorkbenchMode(meta);
    var nodes = buildDiagramNodes(meta);
    var idx = Math.max(0, Math.min(nodes.length - 1, Number(nodeIndex) || 0));
    var node = nodes[idx] || nodes[0];
    var rowIndex = node ? node.rowIndex : 0;
    var chosen = String(selections[rowIndex] || '').trim();
    var prompts = Array.isArray(meta.prompts) ? meta.prompts : [];
    var promptText = prompts[rowIndex] || (node && node.prompt) || ('Task ' + (rowIndex + 1));

    var lines = [];
    lines.push('====================================================================');
    lines.push('LIVE DEVICE INSPECTOR · ' + (node ? node.title.toUpperCase() : 'NODE 1'));
    lines.push('Exam Objective : ' + (meta.lo || meta.examCode || 'CompTIA Performance Simulation'));
    lines.push('Subsystem Role : ' + (node ? node.role : 'Simulation Node'));
    lines.push('Mapped Field   : Row #' + (rowIndex + 1) + ' — ' + promptText);
    lines.push('Live Status    : ' + (chosen ? ('CONFIGURED -> ' + chosen) : 'PENDING CANDIDATE INPUT (—)'));
    lines.push('====================================================================');

    if (meta.inspectorText) {
      lines.push('');
      lines.push('[Captured Device Inspector Feed]');
      lines.push(String(meta.inspectorText).trim());
    }

    var cmdKeys = Object.keys(meta.commands || {});
    if (cmdKeys.length) {
      var sampleCmd = cmdKeys[idx % cmdKeys.length];
      lines.push('');
      lines.push('[Live Telemetry Capture: ' + sampleCmd + ']');
      lines.push(String(meta.commands[sampleCmd]).trim());
    }

    lines.push('');
    if (mode === 'network') {
      lines.push('[Network & Security Telemetry Stream — show interfaces trunk / show ip ospf neighbor]');
      lines.push('Interface   Mode      Encap    Status     Allowed VLANs   OSPF Neighbor');
      lines.push('Gi0/1       trunk     802.1q   trunking   1,10,20         10.0.0.1 (FULL/DR)');
      lines.push('Gi0/2       access    n/a      up/up      VLAN 10         n/a');
      lines.push('Gi0/3       access    n/a      up/up      VLAN 20         n/a');
      lines.push('Syslog Alert: %LINEPROTO-5-UPDOWN / Verify ACL order, VLAN trunk list & gateway reachability.');
    } else if (mode === 'hardware') {
      lines.push('[Hardware & Chassis Sensor Feed — SMART / POST telemetry & Bus Inspector]');
      lines.push('Slot / Bay               Bus Status            PSU Rails (+12V / +5V / +3.3V)');
      lines.push('M2_1 (PCIe 4.0 x4)       NVMe Ready            +12.04V  +5.01V  +3.32V  [OK]');
      lines.push('DIMM A2/B2               Dual-Channel Active   POST Code: 0x00 (Normal)');
      lines.push('RJ-45 / Laser Bay        T568B / Fuser Nominal SMART Health: PASSED (0 media errors)');
    } else {
      lines.push('[System & Security Architecture Feed — bcdedit /enum · icacls · ls -la · Event Viewer]');
      lines.push('Boot/Volume : UEFI Secure Boot Enabled · GPT Partition Map · Check Volume Free Space');
      lines.push('Permissions : icacls / Share & NTFS Effective Access · POSIX drwxr-x--- root:secops');
      lines.push('Pipeline    : Service & Host Firewall Inspector · Event ID 4624/7036 Telemetry Active');
    }

    if (meta.text) {
      lines.push('');
      lines.push('[Scenario Context]');
      lines.push(String(meta.text).trim());
    }

    return lines.join('\n');
  }

  /**
   * Executes a read-only diagnostic command inside the PBQ workbench terminal (pbq-cli).
   */
  function runDiagnosticCommand(rawCmd, meta, selections) {
    meta = meta || {};
    selections = Array.isArray(selections) ? selections : [];
    var cmd = String(rawCmd || '').trim();
    var lower = cmd.toLowerCase();
    var prompts = Array.isArray(meta.prompts) ? meta.prompts : [];
    var optionsByRow = Array.isArray(meta.optionsByRow) ? meta.optionsByRow : [];
    var mode = meta.mode || detectWorkbenchMode(meta);

    if (!cmd) {
      return 'Type a read-only diagnostic command (or type "help" for available commands).';
    }

    // 1. Check exact match in PBQ's own terminal commands if present
    var customCmds = meta.commands || {};
    var customKey = Object.keys(customCmds).find(function (k) {
      return k.toLowerCase() === lower;
    });
    if (customKey) {
      return customCmds[customKey];
    }

    // 2. Built-in workbench diagnostic commands
    if (lower === 'help' || lower === '?') {
      var extraList = Object.keys(customCmds);
      return [
        'Novak LMS™ Read-Only PBQ Diagnostic Console (pbq-cli)',
        'Available commands:',
        '  help                  Show this command reference',
        '  status                Show configuration progress across all simulation rows',
        '  show run              Synthesize running configuration with current candidate selections',
        '  show vlan             Display 802.1Q VLAN table and trunk allowed VLAN telemetry',
        '  show ip route         Display L3 routing table, OSPF neighbors, and ACL summary',
        '  ping [target]         Run simulated ICMP reachability check against scenario endpoints',
        '  nslookup [host]       Query simulated DNS resolver and check for portal/split-DNS',
        '  ipconfig /all         Display host NIC IPv4, mask, gateway, DHCP, and APIPA status',
        '  diskpart              Inspect GPT/MBR disks, EFI partitions, and volume free space',
        '  bootrec               Inspect UEFI/BCD boot manager entries (bcdedit /enum)',
        '  permissions           Inspect NTFS (icacls), SMB share, and POSIX (ls -la) permissions',
        '  inspect <row>         Inspect configuration row # (e.g., inspect 1)'
      ].concat(
        extraList.length ? ['  Scenario commands   : ' + extraList.join(', ')] : []
      ).join('\n');
    }

    if (lower === 'status') {
      var configuredCount = selections.filter(function (v) { return String(v || '').trim().length > 0; }).length;
      var total = prompts.length || selections.length || 1;
      var rowsOut = prompts.map(function (p, i) {
        var val = String(selections[i] || '').trim();
        return '  Row ' + (i + 1) + ' [' + (val ? 'CONFIGURED' : 'PENDING   ') + '] ' + p + ' -> ' + (val || '—');
      });
      return [
        'Simulation Workbench Status (' + mode.toUpperCase() + ' MODE)',
        'Simulation Tasks Configured: ' + configuredCount + ' / ' + total,
        '--------------------------------------------------------------------'
      ].concat(rowsOut).join('\n');
    }

    if (lower === 'show run' || lower === 'show running-config') {
      var cfgLines = [
        'Building configuration...',
        'Current configuration : Novak-PBQ-Workbench (' + (meta.examCode || 'CompTIA-Sim') + ')',
        '!',
        '! Scenario: ' + truncate(meta.text || 'Interactive Performance-Based Question', 72),
        '!'
      ];
      prompts.forEach(function (p, i) {
        var val = String(selections[i] || '').trim();
        cfgLines.push('task-row ' + (i + 1) + ' prompt "' + p + '"');
        cfgLines.push('  candidate-selection ' + (val ? ('"' + val + '"') : 'UNCONFIGURED'));
        cfgLines.push('!');
      });
      if (meta.inspectorText) {
        cfgLines.push('! Device Inspector Snapshot:');
        String(meta.inspectorText).split('\n').forEach(function (ln) {
          cfgLines.push('!   ' + ln);
        });
      }
      cfgLines.push('end');
      return cfgLines.join('\n');
    }

    if (lower === 'show vlan' || lower === 'show vlan brief' || lower === 'show interfaces trunk') {
      if (customCmds['show vlan brief'] || customCmds['show interfaces trunk']) {
        return [
          customCmds['show vlan brief'] || '',
          customCmds['show interfaces trunk'] || ''
        ].filter(Boolean).join('\n\n');
      }
      return [
        'VLAN Name                             Status    Ports',
        '---- -------------------------------- --------- -------------------------------',
        '1    default                          active    Gi0/4-24',
        '10   CORP-STAFF / INTERNAL-SERVERS    active    Gi0/2, WLC-SSID-1',
        '20   USERS-B / VOICE-DATA             active    Gi0/3',
        '99   GUEST-ISOLATED                   active    WLC-SSID-2',
        '',
        'Port        Mode             Encapsulation  Status        Native vlan',
        'Gi0/1       on               802.1q         trunking      1',
        'Vlans allowed on trunk Gi0/1: 1,10 (Verify if VLAN 20 or Guest VLAN needs tagging)'
      ].join('\n');
    }

    if (lower === 'show ip route' || lower === 'show ip ospf neighbor' || lower === 'show access-lists') {
      if (customCmds['show ip route'] || customCmds['show access-lists']) {
        return [
          customCmds['show ip route'] || '',
          customCmds['show access-lists'] || ''
        ].filter(Boolean).join('\n\n');
      }
      return [
        'Codes: C - connected, S - static, O - OSPF, * - candidate default',
        'Gateway of last resort is 203.0.113.1 to network 0.0.0.0',
        'C    10.10.10.0/24 is directly connected, GigabitEthernet0/0.10',
        'C    10.10.20.0/24 is directly connected, GigabitEthernet0/0.20',
        'O    172.16.0.0/24 [110/20] via 10.0.0.2, 00:42:11, GigabitEthernet0/1',
        'S*   0.0.0.0/0 [1/0] via 203.0.113.1',
        '',
        'OSPF Neighbor ID    Pri   State           Dead Time   Address         Interface',
        '10.0.0.2              1   FULL/BDR        00:00:36    10.0.0.2        Gi0/1'
      ].join('\n');
    }

    if (lower === 'ping' || lower.indexOf('ping ') === 0) {
      var target = cmd.slice(4).trim() || '10.10.10.1';
      var pingCustom = Object.keys(customCmds).find(function (k) { return k.toLowerCase().indexOf('ping') === 0; });
      if (pingCustom && !cmd.slice(4).trim()) {
        return customCmds[pingCustom];
      }
      return [
        'Pinging ' + target + ' with 32 bytes of data:',
        'Reply from ' + target + ': bytes=32 time=2ms TTL=64',
        'Reply from ' + target + ': bytes=32 time=1ms TTL=64',
        'Ping statistics for ' + target + ': Packets: Sent = 2, Received = 2, Lost = 0 (0% loss)',
        'Note: ICMP Echo (Layer 3) succeeded. If application traffic fails, check TCP/UDP ACLs, DNS, or service ports.'
      ].join('\n');
    }

    if (lower === 'nslookup' || lower.indexOf('nslookup ') === 0) {
      var nslCustom = Object.keys(customCmds).find(function (k) { return k.toLowerCase().indexOf('nslookup') === 0; });
      if (nslCustom) return customCmds[nslCustom];
      var host = cmd.slice(8).trim() || 'intranet.corp.local';
      return [
        'Server:  dns01.corp.local',
        'Address: 10.10.10.53',
        '',
        'Name:    ' + host,
        'Address: 10.10.10.80',
        'Status:  Authoritative answer (verify captive portal redirect if gateway IP is returned)'
      ].join('\n');
    }

    if (lower === 'ipconfig' || lower === 'ipconfig /all') {
      if (customCmds['ipconfig /all'] || customCmds['ipconfig']) {
        return customCmds['ipconfig /all'] || customCmds['ipconfig'];
      }
      return [
        'Windows IP Configuration',
        'Ethernet adapter Ethernet0:',
        '   Connection-specific DNS Suffix  . : corp.local',
        '   DHCP Enabled. . . . . . . . . . . : Yes',
        '   IPv4 Address. . . . . . . . . . . : 10.10.20.30(Preferred)',
        '   Subnet Mask . . . . . . . . . . . : 255.255.255.0',
        '   Default Gateway . . . . . . . . . : 10.10.20.1',
        '   DNS Servers . . . . . . . . . . . : 10.10.10.53'
      ].join('\n');
    }

    if (lower === 'diskpart' || lower === 'fsutil') {
      var fsCustom = Object.keys(customCmds).find(function (k) { return k.toLowerCase().indexOf('fsutil') === 0; });
      if (fsCustom) return customCmds[fsCustom];
      return [
        'DISKPART> list disk / list volume',
        '  Disk ###  Status         Size     Free     Dyn  Gpt',
        '  --------  -------------  -------  -------  ---  ---',
        '  Disk 0    Online          512 GB     0 B         *   (M2_1 PCIe 4.0 NVMe)',
        '  Disk 1    Online           32 GB     0 B         *   (Volume D: Data/Scratch)',
        '',
        '  Volume ###  Ltr  Label        Fs     Type        Size     Status',
        '  ----------  ---  -----------  -----  ----------  -------  ---------',
        '  Volume 0     C   OS-SYSTEM    NTFS   Partition    511 GB  Healthy (System, Boot)',
        '  Volume 1         EFI-SYSTEM   FAT32  System       512 MB  Healthy',
        '  Volume 2     D   DATA-VOL     NTFS   Partition     32 GB  Healthy (Check free space / quotas)'
      ].join('\n');
    }

    if (lower === 'bootrec' || lower === 'bcdedit' || lower === 'bcdedit /enum') {
      return [
        'Windows Boot Manager (bcdedit /enum · bootrec /scanos)',
        '--------------------------------------------------------------------',
        'identifier              {bootmgr}',
        'device                  partition=\\Device\\HarddiskVolume1 (EFI System Partition)',
        'path                    \\EFI\\Microsoft\\Boot\\bootmgfw.efi',
        'description             Windows Boot Manager (UEFI Mode · Secure Boot: Enabled · CSM: Disabled)',
        'displayorder            {current} (NVMe Boot Manager first after migration)'
      ].join('\n');
    }

    if (lower === 'permissions' || lower === 'icacls' || lower === 'ls -la') {
      var icCustom = Object.keys(customCmds).find(function (k) { return k.toLowerCase().indexOf('icacls') === 0; });
      if (icCustom) {
        return [
          customCmds[icCustom],
          customCmds['net share Finance'] || ''
        ].filter(Boolean).join('\n\n');
      }
      return [
        '[NTFS & SMB Share Effective Permissions — icacls / net share]',
        '  Share Permission : Everyone -> CHANGE / FULL (most restrictive of Share + NTFS wins)',
        '  NTFS ACLs        : BUILTIN\\Administrators:(OI)(CI)(F)',
        '                     CORP\\AuthorizedGroup:(OI)(CI)(M)',
        '                     BUILTIN\\Users: (Removed to prevent unintended inheritance)',
        '',
        '[POSIX Mode Matrix — ls -la]',
        '  drwxr-x---  4 root  secops  4096 Oct 26 12:00 /srv/secure-share',
        '  -rw-r-----  1 root  secops  1820 Oct 26 12:00 /etc/app/config.yaml'
      ].join('\n');
    }

    if (lower === 'inspect' || lower.indexOf('inspect ') === 0) {
      var arg = cmd.slice(7).trim();
      var num = parseInt(arg, 10);
      var rIdx = isNaN(num) ? 0 : Math.max(0, Math.min(prompts.length - 1, num - 1));
      var pLabel = prompts[rIdx] || ('Row ' + (rIdx + 1));
      var curVal = String(selections[rIdx] || '').trim();
      var opts = optionsByRow[rIdx] || [];
      return [
        'Inspecting Configuration Row #' + (rIdx + 1) + ' of ' + (prompts.length || 1),
        '  Prompt            : ' + pLabel,
        '  Current Selection : ' + (curVal || '— (Unconfigured)'),
        '  Available Choices : ' + (opts.length ? opts.join(' | ') : '(Select dropdown options in form below)')
      ].join('\n');
    }

    return [
      'Command "' + cmd + '" is not recognized in this read-only simulation.',
      'Type "help" or click one of the quick-command buttons above (status, show run, show vlan, show ip route, ping, nslookup, ipconfig /all, diskpart, bootrec, permissions, inspect 1).'
    ].join('\n');
  }

  /**
   * Extracts PBQ metadata and current `<select>` values from a question `<section class="... es-pbq">` element.
   */
  function extractMetaFromSection(sectionEl) {
    if (!sectionEl) return {};
    var rootBar = (sectionEl.ownerDocument && sectionEl.ownerDocument.getElementById('examSim')) || null;
    var headerBarText = rootBar ? (rootBar.textContent || '') : '';
    var examMatch = headerBarText.match(/\b(220-1201|220-1202|N10-009|FC0-U71)\b/i);
    var examCode = sectionEl.getAttribute('data-exam-code') || (examMatch ? examMatch[1] : '');

    var h2 = sectionEl.querySelector('h2');
    var loSpan = h2 ? h2.querySelector('.text-muted') : null;
    var lo = sectionEl.getAttribute('data-lo') || (loSpan ? loSpan.textContent.trim() : '');

    var pEl = sectionEl.querySelector('p');
    var text = pEl ? pEl.textContent.trim() : '';

    var rows = Array.prototype.slice.call(sectionEl.querySelectorAll('.es-row'));
    var prompts = [];
    var selections = [];
    var optionsByRow = [];

    rows.forEach(function (r, idx) {
      var lbl = r.querySelector('label');
      var sel = r.querySelector('select');
      prompts.push(lbl ? lbl.textContent.trim() : ('Step ' + (idx + 1)));
      selections.push(sel ? (sel.value || '') : '');
      if (sel && sel.options) {
        var opts = [];
        for (var i = 0; i < sel.options.length; i++) {
          var v = (sel.options[i].value || sel.options[i].textContent || '').trim();
          if (v && v !== '—') opts.push(v);
        }
        optionsByRow.push(opts);
      } else {
        optionsByRow.push([]);
      }
    });

    var nodes = [];
    Array.prototype.slice.call(sectionEl.querySelectorAll('.es-node')).forEach(function (n) {
      nodes.push({
        name: (n.textContent || '').trim(),
        detail: n.getAttribute('data-detail') || ''
      });
    });

    var commands = {};
    Array.prototype.slice.call(sectionEl.querySelectorAll('.es-term template[data-cmd]')).forEach(function (tpl) {
      var c = tpl.getAttribute('data-cmd');
      if (c) {
        commands[c] = (tpl.innerHTML || '')
          .replace(/&lt;/g, '<')
          .replace(/&gt;/g, '>')
          .replace(/&amp;/g, '&');
      }
    });

    var inspectorText = '';
    Array.prototype.slice.call(sectionEl.querySelectorAll('.es-panel > pre.es-out')).forEach(function (pre) {
      var t = (pre.textContent || '').trim();
      if (t) inspectorText += (inspectorText ? '\n\n' : '') + t;
    });

    var pbqType = sectionEl.getAttribute('data-pbq-type') ||
      (sectionEl.querySelector('.es-sim') ? 'sim_pbq' : 'match');

    var meta = {
      qIndex: sectionEl.getAttribute('data-n') || '0',
      examCode: examCode,
      lo: lo,
      text: text,
      prompts: prompts,
      optionsByRow: optionsByRow,
      nodes: nodes,
      commands: commands,
      inspectorText: inspectorText,
      pbqType: pbqType
    };
    meta.mode = detectWorkbenchMode(meta);
    return { meta: meta, selections: selections, rows: rows };
  }

  /**
   * Initializes the interactive PBQ Workbench on a single `.es-pbq` question section.
   */
  function initQuestionWorkbench(sectionEl) {
    if (!sectionEl || sectionEl.getAttribute('data-pbq-wb-ready') === '1') return null;
    var extracted = extractMetaFromSection(sectionEl);
    var meta = extracted.meta;
    var selections = extracted.selections;
    var rows = extracted.rows;
    if (!rows.length) return null;

    sectionEl.setAttribute('data-pbq-wb-ready', '1');
    var qId = meta.qIndex;
    var activeNodeIndex = 0;
    var activeTab = 'visualizer';
    var tpl = MODE_TEMPLATES[meta.mode] || MODE_TEMPLATES.network;
    var nodes = buildDiagramNodes(meta);

    // Ensure or find header progress badge
    var h2 = sectionEl.querySelector('h2');
    var headerBadge = sectionEl.querySelector('[data-pbq-progress]');
    if (!headerBadge && h2) {
      headerBadge = sectionEl.ownerDocument.createElement('span');
      headerBadge.className = 'badge pbq-wb-progress';
      headerBadge.setAttribute('data-pbq-progress', '');
      h2.appendChild(sectionEl.ownerDocument.createTextNode(' '));
      h2.appendChild(headerBadge);
    }

    // Ensure or find workbench host container
    var host = sectionEl.querySelector('[data-pbq-workbench]');
    if (!host) {
      host = sectionEl.ownerDocument.createElement('div');
      host.className = 'pbq-wb';
      host.setAttribute('data-pbq-workbench', '');
      var anchor = sectionEl.querySelector('.es-sim') || rows[0];
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(host, anchor);
      } else {
        sectionEl.appendChild(host);
      }
    } else {
      host.classList.add('pbq-wb');
    }

    var cliPills = DEFAULT_CLI_PILLS.slice();
    Object.keys(meta.commands || {}).forEach(function (c) {
      if (cliPills.indexOf(c) === -1) cliPills.unshift(c);
    });

    function renderShell() {
      var tabButtonsHtml = TAB_NAMES.map(function (t) {
        var on = t.id === activeTab;
        return (
          '<button type="button" role="tab" class="pbq-wb-tab' + (on ? ' is-active' : '') + '" ' +
          'id="pbqWbTab_' + qId + '_' + t.id + '" ' +
          'data-wb-tab="' + t.id + '" ' +
          'aria-controls="pbqWbPanel_' + qId + '_' + t.id + '" ' +
          'aria-selected="' + (on ? 'true' : 'false') + '">' +
          escHtml(t.label) +
          '</button>'
        );
      }).join('');

      var nodePillsHtml = nodes.map(function (n) {
        var on = n.index === activeNodeIndex;
        var cfg = Boolean(String(selections[n.rowIndex] || '').trim());
        return (
          '<button type="button" class="pbq-inspector-pill' +
          (on ? ' is-active' : '') +
          (cfg ? ' pbq-pill-configured' : '') +
          '" data-inspector-node="' + n.index + '">' +
          escHtml(n.canonicalTitle) +
          '</button>'
        );
      }).join('');

      var cliPillsHtml = cliPills.map(function (c) {
        return (
          '<button type="button" class="pbq-cli-pill" data-pbq-cli-cmd="' + escHtml(c) + '">' +
          escHtml(c) +
          '</button>'
        );
      }).join('');

      var activeNode = nodes[activeNodeIndex] || nodes[0];
      var activeRowIdx = activeNode ? activeNode.rowIndex : 0;

      host.innerHTML = [
        '<div class="pbq-wb-header">',
        '  <div class="pbq-wb-title">',
        '    <span>Interactive PBQ Simulation Workbench</span>',
        '    <span class="pbq-wb-mode-pill" data-wb-mode-pill>' + escHtml(tpl.badgeLabel) + '</span>',
        '  </div>',
        '  <span class="pbq-wb-progress" data-wb-progress-mirror>Simulation Tasks Configured: 0 / ' + rows.length + '</span>',
        '</div>',
        '<div class="pbq-wb-tabs" role="tablist" aria-label="PBQ Workbench Views">',
        tabButtonsHtml,
        '</div>',
        '<div class="pbq-wb-panel" role="tabpanel" id="pbqWbPanel_' + qId + '_visualizer" data-wb-panel="visualizer">',
        '  <div class="pbq-wb-stage">',
        '    <div class="pbq-wb-svg-wrap" data-wb-svg-mount>' + renderDiagramSvg(meta, selections, activeNodeIndex) + '</div>',
        '    <div class="pbq-wb-QuickBar">',
        '      <div class="pbq-wb-QuickBar-info" data-wb-quick-info>',
        '        Active Node: <strong>' + escHtml(activeNode ? activeNode.title : 'Node 1') + '</strong> · Mapped to <strong>Row #' + (activeRowIdx + 1) + ' (' + escHtml(activeNode ? activeNode.prompt : '') + ')</strong>',
        '      </div>',
        '      <div class="d-flex flex-wrap gap-2">',
        '        <button type="button" class="btn btn-sm btn-outline-light pbq-inspect-btn" data-wb-open-inspector="' + activeNodeIndex + '">Inspect Node Telemetry</button>',
        '        <button type="button" class="btn btn-sm btn-warning pbq-jump-btn" data-pbq-jump="' + activeRowIdx + '">Jump to Config Field</button>',
        '      </div>',
        '    </div>',
        '  </div>',
        '</div>',
        '<div class="pbq-wb-panel d-none" role="tabpanel" id="pbqWbPanel_' + qId + '_inspector" data-wb-panel="inspector">',
        '  <div class="pbq-inspector-bar">',
        '    <div class="pbq-inspector-node-pills" data-wb-inspector-pills>' + nodePillsHtml + '</div>',
        '    <button type="button" class="btn btn-sm btn-warning pbq-jump-btn" data-pbq-jump="' + activeRowIdx + '" data-wb-inspector-jump>Jump to Config Field</button>',
        '  </div>',
        '  <pre class="pbq-inspector-out" aria-live="polite" data-wb-inspector-out>' + escHtml(buildInspectorTelemetry(meta, activeNodeIndex, selections)) + '</pre>',
        '</div>',
        '<div class="pbq-wb-panel d-none" role="tabpanel" id="pbqWbPanel_' + qId + '_terminal" data-wb-panel="terminal">',
        '  <div class="pbq-cli" data-pbq-cli>',
        '    <div class="pbq-cli-cmds">' + cliPillsHtml + '</div>',
        '    <div class="pbq-cli-input-row">',
        '      <label class="pbq-cli-prompt" for="pbqCliIn_' + qId + '">pbq-cli&gt;</label>',
        '      <input type="text" class="pbq-cli-input" id="pbqCliIn_' + qId + '" data-pbq-cli-input placeholder="Type help, status, show run, show vlan, ping, ipconfig /all, diskpart, inspect 1..." autocomplete="off">',
        '      <button type="button" class="btn btn-sm btn-warning" data-pbq-cli-run>Run</button>',
        '    </div>',
        '    <pre class="pbq-cli-out" aria-live="polite" data-pbq-cli-out>' + escHtml(runDiagnosticCommand('status', meta, selections)) + '</pre>',
        '  </div>',
        '</div>'
      ].join('\n');
    }

    function switchTab(tabId) {
      activeTab = tabId;
      Array.prototype.slice.call(host.querySelectorAll('[data-wb-tab]')).forEach(function (btn) {
        var on = btn.getAttribute('data-wb-tab') === tabId;
        btn.classList.toggle('is-active', on);
        btn.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      Array.prototype.slice.call(host.querySelectorAll('[data-wb-panel]')).forEach(function (panel) {
        var on = panel.getAttribute('data-wb-panel') === tabId;
        panel.classList.toggle('d-none', !on);
      });
    }

    function syncProgressAndRows() {
      selections = rows.map(function (r) {
        var s = r.querySelector('select');
        return s ? (s.value || '') : '';
      });
      var configuredCount = selections.filter(function (v) { return String(v || '').trim().length > 0; }).length;
      var total = rows.length;
      var labelText = 'Simulation Tasks Configured: ' + configuredCount + ' / ' + total;

      [headerBadge, host.querySelector('[data-wb-progress-mirror]')].forEach(function (b) {
        if (!b) return;
        b.textContent = labelText;
        b.classList.toggle('pbq-progress-complete', configuredCount === total && total > 0);
        b.classList.toggle('pbq-progress-partial', configuredCount > 0 && configuredCount < total);
      });

      var activeNode = nodes[activeNodeIndex] || nodes[0];
      var activeRowIdx = activeNode ? activeNode.rowIndex : 0;

      rows.forEach(function (r, idx) {
        var val = String(selections[idx] || '').trim();
        r.setAttribute('data-pbq-row', String(idx));
        r.classList.toggle('pbq-row-configured', val.length > 0);
        r.classList.toggle('is-active', idx === activeRowIdx);
      });

      // Refresh SVG diagram
      var svgMount = host.querySelector('[data-wb-svg-mount]');
      if (svgMount) {
        svgMount.innerHTML = renderDiagramSvg(meta, selections, activeNodeIndex);
      }

      // Refresh quick info bar & jump buttons
      var quickInfo = host.querySelector('[data-wb-quick-info]');
      if (quickInfo && activeNode) {
        var chosenVal = String(selections[activeRowIdx] || '').trim();
        quickInfo.innerHTML =
          'Active Node: <strong>' + escHtml(activeNode.title) + '</strong> · Mapped to <strong>Row #' +
          (activeRowIdx + 1) + ' (' + escHtml(activeNode.prompt) + ')</strong>' +
          (chosenVal ? (' · Configured: <strong>' + escHtml(chosenVal) + '</strong>') : '');
      }

      Array.prototype.slice.call(host.querySelectorAll('[data-pbq-jump]')).forEach(function (btn) {
        btn.setAttribute('data-pbq-jump', String(activeRowIdx));
      });

      // Refresh Inspector pills & output
      Array.prototype.slice.call(host.querySelectorAll('[data-inspector-node]')).forEach(function (pill) {
        var nIdx = parseInt(pill.getAttribute('data-inspector-node'), 10);
        var nObj = nodes[nIdx];
        var cfg = nObj ? Boolean(String(selections[nObj.rowIndex] || '').trim()) : false;
        pill.classList.toggle('is-active', nIdx === activeNodeIndex);
        pill.classList.toggle('pbq-pill-configured', cfg);
      });

      var inspOut = host.querySelector('[data-wb-inspector-out]');
      if (inspOut) {
        inspOut.textContent = buildInspectorTelemetry(meta, activeNodeIndex, selections);
      }
    }

    function selectNode(nodeIdx, focusRow) {
      activeNodeIndex = Math.max(0, Math.min(nodes.length - 1, Number(nodeIdx) || 0));
      syncProgressAndRows();
      var activeNode = nodes[activeNodeIndex] || nodes[0];
      var targetRow = rows[activeNode ? activeNode.rowIndex : 0];
      if (focusRow && targetRow) {
        var sel = targetRow.querySelector('select');
        if (targetRow.scrollIntoView) {
          targetRow.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
        if (sel && sel.focus) {
          sel.focus();
        }
      }
    }

    function executeCli(cmdStr) {
      var cliOut = host.querySelector('[data-pbq-cli-out]');
      if (!cliOut) return;
      var output = runDiagnosticCommand(cmdStr, meta, selections);
      cliOut.textContent = 'pbq-cli> ' + cmdStr + '\n' + output;
    }

    renderShell();
    syncProgressAndRows();

    // Delegated click listener inside the workbench host
    host.addEventListener('click', function (e) {
      var tabBtn = e.target.closest('[data-wb-tab]');
      if (tabBtn) {
        e.preventDefault();
        switchTab(tabBtn.getAttribute('data-wb-tab'));
        return;
      }

      var svgNode = e.target.closest('[data-node-index]');
      if (svgNode) {
        e.preventDefault();
        var nIdx = parseInt(svgNode.getAttribute('data-node-index'), 10);
        selectNode(nIdx, true);
        return;
      }

      var openInspBtn = e.target.closest('[data-wb-open-inspector]');
      if (openInspBtn) {
        e.preventDefault();
        switchTab('inspector');
        return;
      }

      var inspPill = e.target.closest('[data-inspector-node]');
      if (inspPill) {
        e.preventDefault();
        selectNode(parseInt(inspPill.getAttribute('data-inspector-node'), 10), false);
        return;
      }

      var jumpBtn = e.target.closest('[data-pbq-jump]');
      if (jumpBtn) {
        e.preventDefault();
        var rIdx = parseInt(jumpBtn.getAttribute('data-pbq-jump'), 10) || 0;
        var mappedNode = nodes.find(function (n) { return n.rowIndex === rIdx; });
        selectNode(mappedNode ? mappedNode.index : 0, true);
        return;
      }

      var cliPill = e.target.closest('[data-pbq-cli-cmd]');
      if (cliPill) {
        e.preventDefault();
        executeCli(cliPill.getAttribute('data-pbq-cli-cmd'));
        return;
      }

      var cliRunBtn = e.target.closest('[data-pbq-cli-run]');
      if (cliRunBtn) {
        e.preventDefault();
        var inp = host.querySelector('[data-pbq-cli-input]');
        if (inp) {
          executeCli(inp.value);
          inp.value = '';
        }
      }
    });

    // Keyboard accessibility for SVG nodes and CLI input
    host.addEventListener('keydown', function (e) {
      var cliInp = e.target.closest('[data-pbq-cli-input]');
      if (cliInp && e.key === 'Enter') {
        e.preventDefault();
        executeCli(cliInp.value);
        cliInp.value = '';
        return;
      }
      var svgNode = e.target.closest('[data-node-index]');
      if (svgNode && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        selectNode(parseInt(svgNode.getAttribute('data-node-index'), 10), true);
      }
    });

    // Row click & select change synchronization
    rows.forEach(function (r, idx) {
      r.addEventListener('click', function () {
        var mapped = nodes.find(function (n) { return n.rowIndex === idx; });
        if (mapped) {
          activeNodeIndex = mapped.index;
          syncProgressAndRows();
        }
      });
      var sel = r.querySelector('select');
      if (sel) {
        sel.addEventListener('focus', function () {
          var mapped = nodes.find(function (n) { return n.rowIndex === idx; });
          if (mapped) {
            activeNodeIndex = mapped.index;
            syncProgressAndRows();
          }
        });
        sel.addEventListener('change', function () {
          var mapped = nodes.find(function (n) { return n.rowIndex === idx; });
          if (mapped) activeNodeIndex = mapped.index;
          syncProgressAndRows();
        });
      }
    });

    return {
      meta: meta,
      nodes: nodes,
      selectNode: selectNode,
      switchTab: switchTab,
      executeCli: executeCli,
      syncProgressAndRows: syncProgressAndRows
    };
  }

  function initAllWorkbenches(doc) {
    var d = doc || (typeof document !== 'undefined' ? document : null);
    if (!d || !d.querySelectorAll) return [];
    var sections = Array.prototype.slice.call(d.querySelectorAll('.es-q.es-pbq'));
    return sections.map(initQuestionWorkbench).filter(Boolean);
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () { initAllWorkbenches(document); });
    } else {
      initAllWorkbenches(document);
    }
  }

  return {
    TAB_NAMES: TAB_NAMES,
    DEFAULT_CLI_PILLS: DEFAULT_CLI_PILLS,
    MODE_TEMPLATES: MODE_TEMPLATES,
    detectWorkbenchMode: detectWorkbenchMode,
    buildDiagramNodes: buildDiagramNodes,
    renderDiagramSvg: renderDiagramSvg,
    buildInspectorTelemetry: buildInspectorTelemetry,
    runDiagnosticCommand: runDiagnosticCommand,
    extractMetaFromSection: extractMetaFromSection,
    initQuestionWorkbench: initQuestionWorkbench,
    initAllWorkbenches: initAllWorkbenches
  };
});
