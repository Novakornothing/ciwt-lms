/* Stage tabs, desk notes, and the client-side Windows, IOS, and network simulations. */
(function () {
  "use strict";
  var root = document.getElementById("labStages");
  if (!root) return;

  function show(id) {
    root.querySelectorAll(".stage-tab").forEach(function (btn) {
      var on = btn.getAttribute("data-stage") === id;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.querySelectorAll("[data-stage-panel]").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-stage-panel") !== id;
    });
  }
  root.querySelectorAll(".stage-tab").forEach(function (btn) {
    btn.addEventListener("click", function () { show(btn.getAttribute("data-stage")); });
  });

  function noteUrl(stage) {
    var base = root.getAttribute("data-note-url");
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + "stage=" + encodeURIComponent(stage);
  }
  root.addEventListener("click", function (ev) {
    var btn = ev.target.closest("[data-open-note]");
    if (!btn) return;
    var stage = btn.getAttribute("data-open-note");
    var box = root.querySelector('[data-note-for="' + stage + '"]');
    fetch(noteUrl(stage), { credentials: "same-origin" }).then(function (r) { return r.json(); }).then(function (data) {
      if (!box) return;
      box.hidden = false;
      box.textContent = data.text || "";
    }).catch(function () {
      if (box) { box.hidden = false; box.textContent = "The note could not be loaded. Try again."; }
    });
  });

  root.querySelectorAll("form.stage-answer").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var input = form.querySelector("input[name=answer]");
      var out = form.querySelector(".stage-result");
      fetch(root.getAttribute("data-stage-url"), {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stage: form.getAttribute("data-stage"), answer: input ? input.value : "" })
      }).then(function (r) { return r.json(); }).then(function (data) {
        if (out) out.textContent = (data.result && data.result.message) || (data.complete ? "Stage recorded." : "Not yet.");
      }).catch(function () { if (out) out.textContent = "The check did not reach the server."; });
    });
  });

  var sheetBtn = document.getElementById("labSheetBtn");
  var sheet = document.getElementById("labSide");
  var scrim = document.getElementById("labSheetScrim");
  function setSheet(open) {
    if (!sheet) return;
    sheet.classList.toggle("is-open", open);
    if (sheetBtn) sheetBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (scrim) scrim.hidden = !open;
    document.body.classList.toggle("lab-sheet-open", open);
  }
  if (sheetBtn && sheet) {
    sheetBtn.addEventListener("click", function () { setSheet(!sheet.classList.contains("is-open")); });
    if (scrim) scrim.addEventListener("click", function () { setSheet(false); });
    var closer = document.getElementById("labSheetClose");
    if (closer) closer.addEventListener("click", function () { setSheet(false); });
  }

  var DB = "novak-labs";
  function saveLocal(key, value) {
    try {
      var req = indexedDB.open(DB, 1);
      req.onupgradeneeded = function () { req.result.createObjectStore("sims"); };
      req.onsuccess = function () {
        var db = req.result;
        var tx = db.transaction("sims", "readwrite");
        tx.objectStore("sims").put(value, key);
      };
    } catch (e) { /* the simulation still runs without storage */ }
  }

  /* Windows simulation */
  var win = document.getElementById("winSim");
  if (win) {
    var wout = document.getElementById("winSimOut");
    var users = { Trainee: true, labtech: true };
    function wline(text) {
      var p = document.createElement("p");
      p.textContent = text;
      wout.appendChild(p);
      wout.scrollTop = wout.scrollHeight;
    }
    wline("Windows PowerShell — simulation");
    wline("Type help for the commands this simulation implements.");
    function runLocal(line) {
      var low = line.trim().toLowerCase();
      if (!low) return;
      wline("> " + line);
      if (low === "help") {
        wline("hostname, ipconfig /all, ping <destination>, Get-Service <name>, Get-LocalUser");
        wline("Set-DnsClientServerAddress -InterfaceAlias <name> -ServerAddresses <address>");
        wline("Rename-Computer -NewName <name>");
        return;
      }
      if (low === "hostname") { wline("(see Settings for the name this simulation is showing)"); return; }
      if (low.indexOf("ipconfig") === 0) { wline("Ethernet  DNS: read Settings after you apply a server"); return; }
      if (low.indexOf("get-localuser") === 0 || low === "net user") {
        Object.keys(users).forEach(function (name) { wline(name + "  " + (users[name] ? "Enabled" : "Disabled")); });
        return;
      }
      if (low.indexOf("get-service") === 0) { wline("Running  Dhcp"); return; }
      wline("The graded console records the same line when you run it there.");
    }
    document.getElementById("winSimForm").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var input = document.getElementById("winSimIn");
      var line = input.value;
      runLocal(line);
      saveLocal("win-transcript", wout.textContent.slice(-4000));
      input.value = "";
      var cmd = root.getAttribute("data-cmd-url");
      if (cmd && line.trim()) {
        fetch(cmd, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ command: line }) }).catch(function () {});
      }
    });
    win.querySelectorAll("[data-sim-tab]").forEach(function (tab) {
      tab.addEventListener("click", function () {
        win.querySelectorAll("[data-sim-tab]").forEach(function (t) { t.classList.toggle("is-active", t === tab); });
        win.querySelectorAll("[data-sim-panel]").forEach(function (p) {
          p.hidden = p.getAttribute("data-sim-panel") !== tab.getAttribute("data-sim-tab");
        });
      });
    });
    win.querySelectorAll("[data-user-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var name = btn.getAttribute("data-user-toggle");
        users[name] = !users[name];
        btn.textContent = users[name] ? "Disable" : "Enable";
        saveLocal("win-users", users);
      });
    });
    var settings = document.getElementById("winSettingsForm");
    if (settings) {
      settings.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var dns = settings.dns.value.trim();
        var name = settings.name.value.trim();
        var stageUrl = root.getAttribute("data-stage-url");
        if (dns) {
          fetch(stageUrl, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ stage: "assisted", answer: dns }) });
          wline("Simulation DNS set to " + dns);
        }
        if (name) {
          fetch(stageUrl, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ stage: "ticket", answer: name }) });
          wline("Simulation computer name set to " + name);
        }
      });
    }
  }

  /* Cisco IOS-style simulation */
  var ios = document.getElementById("iosSim");
  if (ios) {
    var iout = document.getElementById("iosSimOut");
    var mode = "user";
    var host = "LabDevice";
    var iface = null;
    var vlans = { 1: "default" };
    var ports = { "FastEthernet0/1": { mode: "access", vlan: 1 }, "FastEthernet0/2": { mode: "access", vlan: 1 }, "GigabitEthernet0/0": {}, "GigabitEthernet0/1": {} };
    function iline(text) {
      var p = document.createElement("p");
      p.textContent = text;
      iout.appendChild(p);
      iout.scrollTop = iout.scrollHeight;
    }
    function prompt() {
      var p = host + (mode === "user" ? ">" : "#");
      if (mode === "config") p = host + "(config)#";
      if (mode === "config-if") p = host + "(config-if)#";
      if (mode === "config-vlan") p = host + "(config-vlan)#";
      document.getElementById("iosPrompt").textContent = p;
    }
    iline("Simulation console. enable, configure terminal, interface, vlan, show commands.");
    prompt();
    function normIf(token) {
      var m = String(token || "").toLowerCase().replace(/\s+/g, "").match(/^(fa|fastethernet|gi|gigabitethernet)(\d+)\/(\d+)$/);
      if (!m) return null;
      var kind = m[1].charAt(0) === "g" ? "GigabitEthernet" : "FastEthernet";
      return kind + m[2] + "/" + m[3];
    }
    document.getElementById("iosSimForm").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var input = document.getElementById("iosSimIn");
      var line = input.value.trim();
      input.value = "";
      if (!line) return;
      iline(document.getElementById("iosPrompt").textContent + " " + line);
      var low = line.toLowerCase();
      if (low === "enable" || low === "en") { mode = "priv"; }
      else if (low === "configure terminal" || low === "conf t") { if (mode === "priv" || mode === "config") mode = "config"; else iline("% Privileged mode required."); }
      else if (low === "end") { mode = "priv"; iface = null; }
      else if (low === "exit") { if (mode === "config-if" || mode === "config-vlan") mode = "config"; else if (mode === "config") mode = "priv"; else mode = "user"; }
      else if (low.indexOf("hostname ") === 0 && mode === "config") host = line.split(/\s+/).slice(1).join(" ");
      else if (low.indexOf("vlan ") === 0 && (mode === "config" || mode === "config-vlan")) {
        var id = parseInt(line.split(/\s+/)[1], 10);
        if (id >= 1 && id <= 4094) { vlans[id] = vlans[id] || ("VLAN" + id); mode = "config-vlan"; }
        else iline("% VLAN id 1-4094.");
      } else if (low.indexOf("name ") === 0 && mode === "config-vlan") {
        var last = Object.keys(vlans).pop();
        vlans[last] = line.split(/\s+/).slice(1).join(" ");
      } else if (low.indexOf("interface ") === 0 && mode.indexOf("config") === 0) {
        iface = normIf(line.split(/\s+/).slice(1).join(""));
        if (!iface) iline("% Invalid interface.");
        else { ports[iface] = ports[iface] || {}; mode = "config-if"; }
      } else if (mode === "config-if" && low === "switchport mode access") ports[iface].mode = "access";
      else if (mode === "config-if" && low === "switchport mode trunk") { ports[iface].mode = "trunk"; ports[iface].trunk = true; }
      else if (mode === "config-if" && low.indexOf("switchport access vlan ") === 0) ports[iface].vlan = parseInt(line.split(/\s+/).pop(), 10);
      else if (mode === "config-if" && low.indexOf("ip address ") === 0) {
        var bits = line.split(/\s+/);
        ports[iface].ip = bits[2]; ports[iface].mask = bits[3];
      } else if (mode === "config-if" && (low === "no shutdown" || low === "no shut")) ports[iface].up = true;
      else if (mode === "config" && low.indexOf("ip route ") === 0) ports["route"] = line;
      else if (mode === "config" && low.indexOf("access-list ") === 0) ports["acl"] = (ports["acl"] || []).concat([line]);
      else if (low.indexOf("show vlan") === 0) {
        Object.keys(vlans).forEach(function (id) { iline(id + "  " + vlans[id]); });
      } else if (low.indexOf("show ip interface") === 0 || low.indexOf("show ip int") === 0) {
        ["GigabitEthernet0/0", "GigabitEthernet0/1"].forEach(function (name) {
          var row = ports[name] || {};
          iline(name + "  " + (row.ip || "unassigned") + "  " + (row.up ? "up" : "admin down"));
        });
      } else if (low === "?" || low === "help") iline("enable | configure terminal | interface | vlan | show vlan | show ip interface brief | ip route | access-list");
      else iline("% Unrecognized in this simulation. The graded console has the fuller set.");
      prompt();
      saveLocal("ios-state", { host: host, vlans: vlans, ports: ports, mode: mode });
      var cmd = root.getAttribute("data-cmd-url");
      if (cmd) fetch(cmd, { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ command: line }) }).catch(function () {});
    });
  }

  /* Network canvas */
  var net = document.getElementById("netCanvas");
  if (net) {
    var packet = document.getElementById("netPacket");
    var body = net.querySelector("#netTable tbody");
    var hops = [
      { hop: "PC", header: "Ethernet + IPv4 ICMP echo", ports: "—", x: 55 },
      { hop: "Switch", header: "Ethernet, VLAN tag on a trunk", ports: "—", x: 270 },
      { hop: "Router", header: "IPv4, TTL decreased", ports: "—", x: 430 },
      { hop: "Server", header: "TCP or ICMP reply", ports: "443 or echo", x: 580 }
    ];
    document.getElementById("netSend").addEventListener("click", function () {
      body.textContent = "";
      packet.hidden = false;
      var i = 0;
      function step() {
        if (i >= hops.length) return;
        var row = hops[i];
        packet.setAttribute("cx", String(row.x));
        var tr = document.createElement("tr");
        tr.innerHTML = "<td>" + row.hop + "</td><td>" + row.header + "</td><td>" + row.ports + "</td>";
        body.appendChild(tr);
        i += 1;
        if (i < hops.length) setTimeout(step, 350);
      }
      step();
      saveLocal("net-last", hops.map(function (h) { return h.hop; }));
    });
  }
})();
