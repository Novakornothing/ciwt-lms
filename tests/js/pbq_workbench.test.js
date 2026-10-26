// Run: node --test tests/js/
const test = require('node:test');
const assert = require('node:assert');
const WB = require('../../static/js/pbq-workbench.js');

// ---------------------------------------------------------------------------
// 1. Diagram Mode Detection (network vs hardware vs system)
// ---------------------------------------------------------------------------
test('detectWorkbenchMode: classifies N10-009 and VLAN/OSPF/ACL/Wi-Fi PBQs as network', () => {
  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: 'N10-009',
      lo: 'N10-009 2.2',
      text: 'Users on PC-B (VLAN 20) cannot reach the file server in VLAN 10. Inspect the switch trunk.',
      prompts: ['Faulty device / port', 'Root cause', 'Corrective command']
    }),
    'network'
  );

  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: 'FC0-U71',
      lo: 'FC0-U71 6.1',
      text: 'Configure WPA3-Personal wireless network on VLAN 10 and isolate guest SSID.',
      prompts: ['Encryption for Novak-Staff', 'Isolation for Novak-Guest', 'Router management hardening']
    }),
    'network'
  );
});

test('detectWorkbenchMode: classifies 220-1201 motherboard, M.2 NVMe, PSU, printer, and T568B cable PBQs as hardware', () => {
  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: '220-1201',
      lo: '220-1201 2.1',
      text: 'Terminate a straight-through patch cable to the T568B standard. Inspect the pinout card.',
      prompts: ['Pin 1', 'Pin 2', 'Pin 3', 'Pin 6']
    }),
    'hardware'
  );

  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: '220-1201',
      lo: '220-1201 3.4',
      text: 'A technician installs an M.2 NVMe SSD and a second DIMM RAM kit on the motherboard.',
      prompts: ['Move the NVMe SSD to', 'Side effect to plan for', 'UEFI boot order after cloning']
    }),
    'hardware'
  );

  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: '220-1201',
      lo: '220-1201 3.8',
      text: 'Put the steps for installing a laser printer maintenance kit (fuser, toner, rollers) in order.',
      prompts: ['Step 1', 'Step 2', 'Step 3', 'Step 4']
    }),
    'hardware'
  );
});

test('detectWorkbenchMode: classifies 220-1202 and FC0-U71 OS, NTFS permissions, RDP service, and malware PBQs as system', () => {
  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: '220-1202',
      lo: '220-1202 2.6',
      text: 'A shared folder must give the Finance group change access. Inspect icacls and NTFS permissions.',
      prompts: ['Share permission for Everyone', 'NTFS entry for CORP\\Finance', 'NTFS entry for BUILTIN\\Users']
    }),
    'system'
  );

  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: '220-1202',
      lo: '220-1202 1.6',
      text: 'Remote Desktop to PC-FIN07 fails. Inspect TermService and Get-NetFirewallRule in PowerShell.',
      prompts: ['Setting to change first', 'Firewall rule state', 'Port the rule allows']
    }),
    'system'
  );

  assert.strictEqual(
    WB.detectWorkbenchMode({
      examCode: 'FC0-U71',
      lo: 'FC0-U71 3.1',
      text: 'Shared Windows 11 workstation has runaway render_preview.exe process and 0 bytes free on Volume D: via fsutil.',
      prompts: ['Runaway memory process to stop', 'Why saves to D: fail', 'Preventive fix']
    }),
    'system'
  );
});

// ---------------------------------------------------------------------------
// 2. Diagram Nodes & Interactive SVG Synthesis
// ---------------------------------------------------------------------------
test('buildDiagramNodes & renderDiagramSvg: synthesizes mode-specific interactive nodes and updates live badges', () => {
  const netMeta = {
    examCode: 'N10-009',
    text: 'Configure VLAN 20 trunking and OSPF routing.',
    prompts: ['Faulty device / port', 'Root cause', 'Corrective command']
  };
  const netNodes = WB.buildDiagramNodes(netMeta);
  assert.ok(netNodes.length >= 6);
  const titles = netNodes.map((n) => n.canonicalTitle);
  assert.ok(titles.includes('Core Router'));
  assert.ok(titles.includes('L2/L3 Switch'));
  assert.ok(titles.includes('Firewall / DMZ'));
  assert.ok(titles.includes('RADIUS / DNS Server'));
  assert.ok(titles.includes('WLC / APs'));
  assert.ok(titles.includes('Branch Subnets'));

  // Initial unconfigured SVG
  const svgEmpty = WB.renderDiagramSvg(netMeta, ['', '', ''], 0);
  assert.ok(svgEmpty.includes('<svg class="pbq-wb-svg"'));
  assert.ok(svgEmpty.includes('data-wb-mode="network"'));
  assert.ok(svgEmpty.includes('Task #1: Unconfigured'));
  assert.ok(!svgEmpty.includes('pbq-node-configured'));

  // Configured SVG updates with green/configured badges and chosen values
  const svgConfigured = WB.renderDiagramSvg(
    netMeta,
    ['SW1 Gi0/1 (trunk uplink)', 'VLAN 20 not allowed on trunk', ''],
    1
  );
  assert.ok(svgConfigured.includes('pbq-node-configured'));
  assert.ok(svgConfigured.includes('✓ SW1 Gi0/1 (trunk uplink)'));
  assert.ok(svgConfigured.includes('✓ VLAN 20 not allowed on'));
  assert.ok(svgConfigured.includes('pbq-link-configured'));

  // Hardware SVG check
  const hwMeta = {
    examCode: '220-1201',
    text: 'Inspect motherboard M.2 NVMe slot, PSU rails, and RJ-45 patch panel.',
    prompts: ['Slot 1', 'Slot 2', 'Slot 3']
  };
  const hwSvg = WB.renderDiagramSvg(hwMeta, ['M2_1 (PCIe 4.0 x4)', '', ''], 0);
  assert.ok(hwSvg.includes('data-wb-mode="hardware"'));
  assert.ok(hwSvg.includes('CPU/PCIe/DIMM'));
  assert.ok(hwSvg.includes('PSU Rails'));
  assert.ok(hwSvg.includes('Laser Imaging Assembly'));
  assert.ok(hwSvg.includes('RJ-45/Fiber Patch Panel'));
  assert.ok(hwSvg.includes('Hypervisor Host'));

  // System SVG check
  const sysMeta = {
    examCode: '220-1202',
    text: 'Inspect NTFS permissions with icacls and UEFI/GPT partition map.',
    prompts: ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4']
  };
  const sysSvg = WB.renderDiagramSvg(sysMeta, ['Modify', '', '', ''], 0);
  assert.ok(sysSvg.includes('data-wb-mode="system"'));
  assert.ok(sysSvg.includes('UEFI/GPT Partition Map'));
  assert.ok(sysSvg.includes('NTFS/POSIX Permission Matrix'));
  assert.ok(sysSvg.includes('Service/GPO Pipeline'));
  assert.ok(sysSvg.includes('SQL Schema / Logic Trace'));
});

// ---------------------------------------------------------------------------
// 3. Live Device Inspector & Telemetry Feed
// ---------------------------------------------------------------------------
test('buildInspectorTelemetry: extracts scenario telemetry and reflects active node & candidate configuration', () => {
  const meta = {
    examCode: 'N10-009',
    lo: 'N10-009 2.2',
    text: 'Users on PC-B (VLAN 20) cannot reach FS1 in VLAN 10.',
    prompts: ['Faulty device / port', 'Root cause', 'Corrective command'],
    commands: {
      'show interfaces trunk': 'Port Gi0/1 allowed VLANs: 1,10'
    },
    inspectorText: 'interface Gi0/1\n switchport mode trunk'
  };

  const outPending = WB.buildInspectorTelemetry(meta, 0, ['', '', '']);
  assert.ok(outPending.includes('LIVE DEVICE INSPECTOR'));
  assert.ok(outPending.includes('Row #1 — Faulty device / port'));
  assert.ok(outPending.includes('PENDING CANDIDATE INPUT'));
  assert.ok(outPending.includes('Port Gi0/1 allowed VLANs: 1,10'));
  assert.ok(outPending.includes('switchport mode trunk'));
  assert.ok(outPending.includes('show interfaces trunk / show ip ospf neighbor'));

  const outConfigured = WB.buildInspectorTelemetry(meta, 0, ['SW1 Gi0/1 (trunk uplink)', '', '']);
  assert.ok(outConfigured.includes('CONFIGURED -> SW1 Gi0/1 (trunk uplink)'));
});

// ---------------------------------------------------------------------------
// 4. Interactive Diagnostic Command Console (pbq-cli)
// ---------------------------------------------------------------------------
test('runDiagnosticCommand: executes help, status, show run, show vlan, show ip route, ping, nslookup, ipconfig /all, diskpart, bootrec, permissions, and inspect <row>', () => {
  const meta = {
    examCode: 'N10-009',
    text: 'Troubleshoot inter-VLAN routing between VLAN 10 and VLAN 20.',
    prompts: ['Faulty device / port', 'Root cause', 'Corrective command'],
    optionsByRow: [
      ['SW1 Gi0/1 (trunk uplink)', 'R1 Gi0/0.10 subinterface'],
      ['VLAN 20 not allowed on trunk', 'Wrong gateway'],
      ['switchport trunk allowed vlan add 20', 'no switchport']
    ],
    commands: {
      'show interfaces gi0/3 switchport': 'Access Mode VLAN: 20 (USERS-B)'
    }
  };
  const selections = ['SW1 Gi0/1 (trunk uplink)', '', 'switchport trunk allowed vlan add 20'];

  const helpOut = WB.runDiagnosticCommand('help', meta, selections);
  assert.ok(helpOut.includes('show run') && helpOut.includes('diskpart') && helpOut.includes('inspect <row>'));

  const statusOut = WB.runDiagnosticCommand('status', meta, selections);
  assert.ok(statusOut.includes('Simulation Tasks Configured: 2 / 3'));
  assert.ok(statusOut.includes('SW1 Gi0/1 (trunk uplink)'));

  const runOut = WB.runDiagnosticCommand('show run', meta, selections);
  assert.ok(runOut.includes('candidate-selection "SW1 Gi0/1 (trunk uplink)"'));
  assert.ok(runOut.includes('candidate-selection UNCONFIGURED'));

  assert.ok(WB.runDiagnosticCommand('show vlan', meta, selections).includes('802.1q'));
  assert.ok(WB.runDiagnosticCommand('show ip route', meta, selections).includes('Gateway of last resort'));
  assert.ok(WB.runDiagnosticCommand('ping 10.10.10.5', meta, selections).includes('Reply from 10.10.10.5'));
  assert.ok(WB.runDiagnosticCommand('nslookup intranet.corp.local', meta, selections).includes('intranet.corp.local'));
  assert.ok(WB.runDiagnosticCommand('ipconfig /all', meta, selections).includes('IPv4 Address'));
  assert.ok(WB.runDiagnosticCommand('diskpart', meta, selections).includes('DISKPART>'));
  assert.ok(WB.runDiagnosticCommand('bootrec', meta, selections).includes('Windows Boot Manager'));
  assert.ok(WB.runDiagnosticCommand('permissions', meta, selections).includes('NTFS'));

  const inspectOut = WB.runDiagnosticCommand('inspect 1', meta, selections);
  assert.ok(inspectOut.includes('Inspecting Configuration Row #1 of 3'));
  assert.ok(inspectOut.includes('SW1 Gi0/1 (trunk uplink)'));

  // Custom PBQ command passthrough
  const customOut = WB.runDiagnosticCommand('show interfaces gi0/3 switchport', meta, selections);
  assert.strictEqual(customOut, 'Access Mode VLAN: 20 (USERS-B)');
});

// ---------------------------------------------------------------------------
// 5. DOM Synchronization (Progress Counter, Row Sync, Tabs & CLI)
// ---------------------------------------------------------------------------
test('initQuestionWorkbench: synchronizes progress counter, SVG badges, inspector, and rows on DOM events', () => {
  function makeMockEnv() {
    function makeClassList(initial) {
      const set = new Set((initial || '').split(/\s+/).filter(Boolean));
      return {
        add: (...cls) => cls.forEach((c) => set.add(c)),
        remove: (...cls) => cls.forEach((c) => set.delete(c)),
        toggle: (c, force) => {
          const on = force === undefined ? !set.has(c) : Boolean(force);
          if (on) set.add(c); else set.delete(c);
          return on;
        },
        contains: (c) => set.has(c),
        toString: () => Array.from(set).join(' ')
      };
    }

    const listeners = new Map();
    function addListener(el, type, fn) {
      if (!listeners.has(el)) listeners.set(el, {});
      const map = listeners.get(el);
      (map[type] = map[type] || []).push(fn);
    }
    function trigger(el, type, evtObj) {
      const map = listeners.get(el) || {};
      (map[type] || []).forEach((fn) => fn(evtObj || { target: el, preventDefault() {} }));
    }

    const headerBadge = {
      textContent: 'Simulation Tasks Configured: 0 / 2',
      classList: makeClassList('badge pbq-wb-progress')
    };
    const progressMirror = {
      textContent: '',
      classList: makeClassList('pbq-wb-progress')
    };
    const svgMount = { innerHTML: '' };
    const quickInfo = { innerHTML: '' };
    const jumpBtn = {
      attrs: { 'data-pbq-jump': '0' },
      setAttribute(k, v) { this.attrs[k] = v; },
      getAttribute(k) { return this.attrs[k]; }
    };
    const inspOut = { textContent: '' };
    const cliOut = { textContent: '' };
    const cliInput = { value: 'status' };

    const tabVis = {
      attrs: { 'data-wb-tab': 'visualizer', 'aria-selected': 'true' },
      classList: makeClassList('pbq-wb-tab is-active'),
      getAttribute(k) { return this.attrs[k]; },
      setAttribute(k, v) { this.attrs[k] = v; }
    };
    const tabInsp = {
      attrs: { 'data-wb-tab': 'inspector', 'aria-selected': 'false' },
      classList: makeClassList('pbq-wb-tab'),
      getAttribute(k) { return this.attrs[k]; },
      setAttribute(k, v) { this.attrs[k] = v; }
    };
    const panelVis = {
      attrs: { 'data-wb-panel': 'visualizer' },
      classList: makeClassList('pbq-wb-panel'),
      getAttribute(k) { return this.attrs[k]; }
    };
    const panelInsp = {
      attrs: { 'data-wb-panel': 'inspector' },
      classList: makeClassList('pbq-wb-panel d-none'),
      getAttribute(k) { return this.attrs[k]; }
    };

    const host = {
      innerHTML: '',
      classList: makeClassList('pbq-wb'),
      addEventListener(type, fn) { addListener(this, type, fn); },
      querySelector(sel) {
        if (sel === '[data-wb-progress-mirror]') return progressMirror;
        if (sel === '[data-wb-svg-mount]') return svgMount;
        if (sel === '[data-wb-quick-info]') return quickInfo;
        if (sel === '[data-wb-inspector-out]') return inspOut;
        if (sel === '[data-pbq-cli-out]') return cliOut;
        if (sel === '[data-pbq-cli-input]') return cliInput;
        return null;
      },
      querySelectorAll(sel) {
        if (sel === '[data-pbq-jump]') return [jumpBtn];
        if (sel === '[data-wb-tab]') return [tabVis, tabInsp];
        if (sel === '[data-wb-panel]') return [panelVis, panelInsp];
        return [];
      }
    };

    function makeRow(promptText, opts, initialVal) {
      let focused = false;
      const selectEl = {
        value: initialVal || '',
        options: [{ value: '', textContent: '—' }].concat(opts.map((o) => ({ value: o, textContent: o }))),
        focus() { focused = true; },
        isFocused() { return focused; },
        addEventListener(type, fn) { addListener(this, type, fn); }
      };
      const rowEl = {
        attrs: {},
        classList: makeClassList('es-row'),
        setAttribute(k, v) { this.attrs[k] = v; },
        getAttribute(k) { return this.attrs[k]; },
        scrollIntoView() {},
        querySelector(sel) {
          if (sel === 'label') return { textContent: promptText };
          if (sel === 'select') return selectEl;
          return null;
        },
        addEventListener(type, fn) { addListener(this, type, fn); }
      };
      return { rowEl, selectEl };
    }

    const r0 = makeRow('Faulty device / port', ['SW1 Gi0/1 (trunk uplink)', 'PC-B NIC'], '');
    const r1 = makeRow('Corrective command', ['switchport trunk allowed vlan add 20', 'shutdown'], '');

    const sectionEl = {
      attrs: { 'data-n': '0', 'data-exam-code': 'N10-009', 'data-lo': 'N10-009 2.2', 'data-pbq-type': 'sim_pbq' },
      ownerDocument: { getElementById: () => ({ textContent: 'CompTIA Network+ (N10-009)' }) },
      getAttribute(k) { return this.attrs[k] || null; },
      setAttribute(k, v) { this.attrs[k] = v; },
      querySelector(sel) {
        if (sel === 'h2') return { querySelector: () => ({ textContent: 'N10-009 2.2' }) };
        if (sel === 'p') return { textContent: 'Users on PC-B (VLAN 20) cannot reach VLAN 10.' };
        if (sel === '[data-pbq-progress]') return headerBadge;
        if (sel === '[data-pbq-workbench]') return host;
        return null;
      },
      querySelectorAll(sel) {
        if (sel === '.es-row') return [r0.rowEl, r1.rowEl];
        return [];
      }
    };

    return { sectionEl, r0, r1, headerBadge, progressMirror, svgMount, inspOut, cliOut, tabInsp, panelInsp, trigger };
  }

  const env = makeMockEnv();
  const ctrl = WB.initQuestionWorkbench(env.sectionEl);
  assert.ok(ctrl);
  assert.strictEqual(env.headerBadge.textContent, 'Simulation Tasks Configured: 0 / 2');
  assert.ok(env.svgMount.innerHTML.includes('data-wb-mode="network"'));

  // Select a value on Row 1 and trigger change
  env.r0.selectEl.value = 'SW1 Gi0/1 (trunk uplink)';
  env.trigger(env.r0.selectEl, 'change');
  assert.strictEqual(env.headerBadge.textContent, 'Simulation Tasks Configured: 1 / 2');
  assert.ok(env.r0.rowEl.classList.contains('pbq-row-configured'));
  assert.ok(env.svgMount.innerHTML.includes('✓ SW1 Gi0/1 (trunk uplink)'));

  // Select a value on Row 2 and verify complete state
  env.r1.selectEl.value = 'switchport trunk allowed vlan add 20';
  env.trigger(env.r1.selectEl, 'change');
  assert.strictEqual(env.headerBadge.textContent, 'Simulation Tasks Configured: 2 / 2');
  assert.ok(env.headerBadge.classList.contains('pbq-progress-complete'));

  // Click node 1 and verify row 1 is focused
  ctrl.selectNode(1, true);
  assert.strictEqual(env.r1.selectEl.isFocused(), true);
  assert.ok(env.inspOut.textContent.includes('Row #2 — Corrective command'));

  // Switch to inspector tab and execute CLI command
  ctrl.switchTab('inspector');
  assert.strictEqual(env.tabInsp.getAttribute('aria-selected'), 'true');
  assert.strictEqual(env.panelInsp.classList.contains('d-none'), false);

  ctrl.executeCli('show run');
  assert.ok(env.cliOut.textContent.includes('pbq-cli> show run'));
  assert.ok(env.cliOut.textContent.includes('switchport trunk allowed vlan add 20'));
});
