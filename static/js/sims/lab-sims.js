/* In-page Windows, Cisco IOS-style, and network-view simulations.
   They run only in this browser, are labeled as simulations, and never send commands to the lab or change its grade. */
(function () {
  "use strict";
  if (!document.getElementById("labSims")) return;

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
    var sim = {
      hostname: "NOVAK-W11-07",
      ipv4: "10.20.30.47",
      mask: "255.255.255.0",
      gateway: "10.20.30.1",
      dns: ["10.20.30.10", "10.20.30.11"],
      mac: "00-1A-2B-AA-BB-07",
      dhcp: true,
      services: {
        Dhcp: ["Running", "DHCP Client"],
        Dnscache: ["Running", "DNS Client"],
        Spooler: ["Running", "Print Spooler"],
        WinDefend: ["Running", "Microsoft Defender Antivirus Service"]
      },
      users: { Trainee: true, labtech: true }
    };
    function wline(text) {
      var p = document.createElement("p");
      p.textContent = text;
      wout.appendChild(p);
      wout.scrollTop = wout.scrollHeight;
    }
    function padLabel(label) {
      var dots = " . . . . . . . . . . . . . . . . . . . . . . . . . ";
      return "   " + (label + dots).slice(0, 36) + ": ";
    }
    wline("Windows PowerShell");
    wline("Copyright (C) Microsoft Corporation. Simulation — not a Windows computer.");
    wline("");
    function winKnown(low) {
      if (low === "help" || low === "hostname" || low === "get-localuser" || low === "net user") return true;
      if (low.indexOf("ipconfig") === 0 || low.indexOf("ping ") === 0 || low === "ping") return true;
      if (low.indexOf("get-service") === 0) return true;
      if (low.indexOf("set-dnsclientserveraddress") === 0) return true;
      if (low.indexOf("rename-computer") === 0) return true;
      return false;
    }
    function runLocal(line) {
      var raw = line.trim();
      var low = raw.toLowerCase();
      if (!low) return false;
      wline("PS C:\\Users\\Trainee> " + raw);
      if (!winKnown(low)) {
        wline("not available in this simulation");
        return false;
      }
      if (low === "help") {
        wline("Implemented here: hostname, ipconfig, ipconfig /all, ping <destination>,");
        wline("Get-Service <Name>, Get-LocalUser,");
        wline("Set-DnsClientServerAddress -InterfaceAlias <name> -ServerAddresses <address>,");
        wline("Rename-Computer -NewName <name>");
        wline("Anything else: not available in this simulation.");
        return true;
      }
      if (low === "hostname") { wline(sim.hostname); return true; }
      if (low === "ipconfig" || low === "ipconfig /all") {
        var full = low.indexOf("/all") >= 0;
        wline("Windows IP Configuration");
        wline("");
        if (full) wline(padLabel("Host Name") + sim.hostname);
        wline("Ethernet adapter Ethernet:");
        wline("");
        if (full) wline(padLabel("Physical Address") + sim.mac);
        if (full) wline(padLabel("DHCP Enabled") + (sim.dhcp ? "Yes" : "No"));
        wline(padLabel("IPv4 Address") + sim.ipv4);
        wline(padLabel("Subnet Mask") + sim.mask);
        wline(padLabel("Default Gateway") + sim.gateway);
        if (full) {
          sim.dns.forEach(function (d, i) {
            wline(padLabel(i === 0 ? "DNS Servers" : "") + d);
          });
        }
        return true;
      }
      if (low.indexOf("ipconfig ") === 0) {
        wline("not available in this simulation");
        return false;
      }
      if (low === "ping") {
        wline("Usage: ping [-n count] target_name");
        return true;
      }
      if (low.indexOf("ping ") === 0) {
        var target = raw.split(/\s+/).pop();
        var local = target === "127.0.0.1" || target === "localhost" || target === sim.ipv4 || target === sim.gateway || sim.dns.indexOf(target) >= 0;
        wline("Pinging " + target + " with 32 bytes of data:");
        var i;
        for (i = 0; i < 4; i++) {
          wline(local
            ? "Reply from " + target + ": bytes=32 time<1ms TTL=128"
            : "Request timed out.");
        }
        wline("");
        wline("Ping statistics for " + target + ":");
        wline(local
          ? "    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),"
          : "    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),");
        return true;
      }
      if (low.indexOf("get-service") === 0) {
        var parts = raw.split(/\s+/);
        var want = parts.length > 1 ? parts[1] : "";
        var names = Object.keys(sim.services).filter(function (n) {
          return !want || n.toLowerCase() === want.toLowerCase();
        });
        if (!names.length) {
          wline("Get-Service : Cannot find any service with service name '" + want + "'.");
          return true;
        }
        wline("Status   Name         DisplayName");
        wline("------   ----         -----------");
        names.forEach(function (n) {
          var row = sim.services[n];
          wline(row[0] + "  " + n + "  " + row[1]);
        });
        return true;
      }
      if (low === "net user") {
        wline("User accounts for \\\\" + sim.hostname);
        wline("-------------------------------------------------------------------------------");
        wline(Object.keys(sim.users).join("                "));
        wline("The command completed successfully.");
        return true;
      }
      if (low === "get-localuser") {
        wline("Name       Enabled");
        wline("----       -------");
        Object.keys(sim.users).forEach(function (name) {
          wline(name + "  " + (sim.users[name] ? "True" : "False"));
        });
        return true;
      }
      if (low.indexOf("set-dnsclientserveraddress") === 0) {
        var m = raw.match(/-ServerAddresses\s+(\S+)/i);
        if (!m) {
          wline("Set-DnsClientServerAddress : Missing an argument for parameter 'ServerAddresses'.");
          return true;
        }
        sim.dns = m[1].replace(/['"()]/g, "").split(",").filter(Boolean);
        return true;
      }
      if (low.indexOf("rename-computer") === 0) {
        var nm = raw.match(/-NewName\s+(\S+)/i);
        if (!nm) {
          wline("Rename-Computer : Missing an argument for parameter 'NewName'.");
          return true;
        }
        sim.hostname = nm[1].replace(/['"]/g, "");
        wline("WARNING: The changes will take effect after you restart the computer.");
        wline("This simulation applies the new name now, so hostname already shows it.");
        return true;
      }
      wline("not available in this simulation");
      return false;
    }
    document.getElementById("winSimForm").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var input = document.getElementById("winSimIn");
      var line = input.value;
      runLocal(line);
      saveLocal("win-transcript", wout.textContent.slice(-4000));
      input.value = "";
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
        sim.users[name] = !sim.users[name];
        btn.textContent = sim.users[name] ? "Disable" : "Enable";
        saveLocal("win-users", sim.users);
      });
    });
    var settings = document.getElementById("winSettingsForm");
    if (settings) {
      settings.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var dns = settings.dns.value.trim();
        var name = settings.name.value.trim();
        if (dns) {
          if (!/^\d{1,3}(\.\d{1,3}){3}$/.test(dns)) { wline("Settings: the DNS server must be an IPv4 address such as 10.20.30.10."); return; }
          sim.dns = [dns];
          wline("Settings: DNS server for Ethernet is now " + dns + ".");
        }
        if (name) {
          sim.hostname = name;
          wline("Settings: computer name is now " + name + ". A real PC applies a rename after a restart.");
        }
        saveLocal("win-settings", { dns: sim.dns, hostname: sim.hostname });
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
    iline("Press RETURN to get started. This is a simulation, not Cisco software.");
    prompt();
    var editVlan = null;
    var routes = [];
    var acls = [];
    var banners = {};
    var kind = ios.getAttribute("data-kind") || "switch";
    function normIf(token) {
      var m = String(token || "").toLowerCase().replace(/\s+/g, "").match(/^(fa|fastethernet|gi|gigabitethernet)(\d+)\/(\d+)$/);
      if (!m) return null;
      var nic = m[1].charAt(0) === "g" ? "GigabitEthernet" : "FastEthernet";
      return nic + m[2] + "/" + m[3];
    }
    function shortIf(name) {
      return String(name).replace("FastEthernet", "Fa").replace("GigabitEthernet", "Gi");
    }
    function pad(text, n) {
      text = String(text);
      return text.length >= n ? text.slice(0, n) : text + " ".repeat(n - text.length);
    }
    function invalid() { iline("% Invalid input detected at '^' marker."); }
    function showVlan() {
      iline("VLAN Name                             Status    Ports");
      iline("---- -------------------------------- --------- -------------------------------");
      var by = {};
      Object.keys(ports).forEach(function (name) {
        var p = ports[name];
        if (!p || p.trunk || p.mode === "trunk") return;
        var id = String(p.vlan || 1);
        (by[id] = by[id] || []).push(shortIf(name));
      });
      Object.keys(vlans).sort(function (a, b) { return Number(a) - Number(b); }).forEach(function (id) {
        iline(pad(id, 4) + " " + pad(vlans[id], 32) + " " + pad("active", 9) + " " + (by[id] || []).join(", "));
      });
    }
    function showIpInt() {
      iline("Interface                  IP-Address      OK? Method Status                Protocol");
      ["GigabitEthernet0/0", "GigabitEthernet0/1"].forEach(function (name) {
        var row = ports[name] || {};
        var up = !!row.up;
        var ip = row.ip || "unassigned";
        var method = row.ip ? "manual" : "unset";
        var status = up ? "up" : "administratively down";
        var proto = up ? "up" : "down";
        iline(pad(shortIf(name), 26) + " " + pad(ip, 15) + " YES " + pad(method, 6) + " " + pad(status, 21) + " " + proto);
      });
    }
    document.getElementById("iosSimForm").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var input = document.getElementById("iosSimIn");
      var line = input.value.trim();
      input.value = "";
      if (!line) return;
      iline(document.getElementById("iosPrompt").textContent + line);
      var low = line.toLowerCase();
      if (low === "enable" || low === "en") {
        if (mode === "user") mode = "priv";
        else if (mode !== "priv") invalid();
      } else if (low === "disable") {
        if (mode === "priv") mode = "user";
        else invalid();
      } else if (low === "configure terminal" || low === "conf t") {
        if (mode === "priv") { mode = "config"; iface = null; editVlan = null; }
        else invalid();
      } else if (low === "end") {
        if (mode === "user" || mode === "priv") invalid();
        else { mode = "priv"; iface = null; editVlan = null; }
      } else if (low === "exit") {
        if (mode === "config-if" || mode === "config-vlan") { mode = "config"; iface = null; editVlan = null; }
        else if (mode === "config") mode = "priv";
        else if (mode === "priv") mode = "user";
        else invalid();
      } else if (low.indexOf("hostname ") === 0) {
        if (mode !== "config") invalid();
        else host = line.split(/\s+/).slice(1).join(" ");
      } else if (low.indexOf("vlan ") === 0) {
        if (kind !== "switch" || (mode !== "config" && mode !== "config-vlan")) { if (kind !== "switch") { iline("not available in this simulation"); } else invalid(); }
        else {
          var vid = parseInt(line.split(/\s+/)[1], 10);
          if (!(vid >= 1 && vid <= 4094)) iline("% VLAN id 1-4094.");
          else { vlans[vid] = vlans[vid] || ("VLAN" + vid); editVlan = vid; mode = "config-vlan"; iface = null; }
        }
      } else if (low.indexOf("name ") === 0 && mode === "config-vlan") {
        if (editVlan == null) invalid();
        else vlans[editVlan] = line.split(/\s+/).slice(1).join(" ");
      } else if (low.indexOf("interface ") === 0) {
        if (mode !== "config" && mode !== "config-if") invalid();
        else {
          iface = normIf(line.replace(/^interface\s+/i, ""));
          if (!iface) iline("% Invalid interface. Example: interface FastEthernet0/1");
          else { ports[iface] = ports[iface] || { mode: "access", vlan: 1 }; mode = "config-if"; editVlan = null; }
        }
      } else if (mode === "config-if" && (low === "switchport mode access" || low === "switchport mode trunk" || low.indexOf("switchport access vlan ") === 0 || low.indexOf("switchport trunk allowed vlan ") === 0 || low.indexOf("switchport port-security") === 0)) {
        if (kind !== "switch") { iline("not available in this simulation"); }
        else if (low === "switchport mode access") { ports[iface].mode = "access"; ports[iface].trunk = false; }
        else if (low === "switchport mode trunk") { ports[iface].mode = "trunk"; ports[iface].trunk = true; }
        else if (low.indexOf("switchport access vlan ") === 0) {
          var av = parseInt(line.split(/\s+/).pop(), 10);
          ports[iface].vlan = av; ports[iface].mode = "access"; ports[iface].trunk = false;
          vlans[av] = vlans[av] || ("VLAN" + av);
        } else if (low.indexOf("switchport trunk allowed vlan ") === 0) {
          ports[iface].allowed = line.split(/\s+/).pop().split(",").map(function (n) { return parseInt(n, 10); }).filter(function (n) { return n; });
        } else ports[iface].portsec = true;
      } else if (mode === "config-if" && low.indexOf("ip address ") === 0) {
        var bits = line.split(/\s+/);
        if (bits.length < 4 || (bits[2].match(/\./g) || []).length !== 3 || (bits[3].match(/\./g) || []).length !== 3) {
          iline("% Incomplete command. Example: ip address 10.1.1.1 255.255.255.0");
        } else { ports[iface].ip = bits[2]; ports[iface].mask = bits[3]; }
      } else if (mode === "config-if" && (low === "no shutdown" || low === "no shut")) ports[iface].up = true;
      else if (mode === "config-if" && low === "shutdown") ports[iface].up = false;
      else if (mode === "config-if" && low.indexOf("description ") === 0) ports[iface].desc = line.split(/\s+/).slice(1).join(" ");
      else if (mode === "config" && low.indexOf("ip route ") === 0) {
        var rp = line.split(/\s+/);
        if (rp.length < 5) iline("% Incomplete command. Example: ip route 0.0.0.0 0.0.0.0 10.1.1.2");
        else routes.push({ dest: rp[2], mask: rp[3], hop: rp[4] });
      } else if (mode === "config" && low.indexOf("access-list ") === 0) acls.push(line);
      else if (mode === "config" && /^banner (login|motd) \S/.test(low)) {
        var bm = line.match(/^banner\s+(login|motd)\s+(.*)$/i);
        var txt = bm[2];
        var d = txt.charAt(0);
        if (txt.length > 1 && txt.lastIndexOf(d) > 0 && !/[A-Za-z0-9]/.test(d)) txt = txt.slice(1, txt.lastIndexOf(d));
        banners[bm[1].toLowerCase()] = txt;
      }
      else if (low === "show banner login" || low === "sh banner login" || low === "show banner motd" || low === "sh banner motd") {
        if (mode !== "user" && mode !== "priv") invalid();
        else { var bk = low.slice(-5) === "login" ? "login" : "motd"; if (banners[bk]) iline(banners[bk]); }
      }
      else if (low === "show vlan brief" || low === "show vlan" || low === "sh vlan brief" || low === "sh vlan") showVlan();
      else if (low === "show ip interface brief" || low === "sh ip int br" || low === "show ip int brief") showIpInt();
      else if (low === "show ip route" || low === "sh ip route") {
        iline("Codes: S - static");
        var def = routes.filter(function (r) { return r.dest === "0.0.0.0"; })[0];
        iline(def ? "Gateway of last resort is " + def.hop + " to network 0.0.0.0" : "Gateway of last resort is not set");
        iline("");
        routes.forEach(function (r) {
          iline("S        " + r.dest + " " + r.mask + " [1/0] via " + r.hop);
        });
      } else if (low === "?" || low === "help") {
        iline("User: enable");
        iline("Privileged: configure terminal, disable, show vlan brief, show ip interface brief, show ip route, show banner login, show banner motd");
        iline("Config: hostname, interface, vlan, ip route, access-list, banner login, banner motd, end");
        iline("Interface: ip address, no shutdown, description, switchport (switch labs)");
        iline("Other input: not available in this simulation");
      } else {
        iline("not available in this simulation");
      }
      prompt();
      saveLocal("ios-state", { host: host, mode: mode, vlans: vlans, ports: ports, routes: routes, banners: banners });
    });
  }

  /* Network canvas */
  var net = document.getElementById("netCanvas");
  if (net) {
    var packet = document.getElementById("netPacket");
    var body = net.querySelector("#netTable tbody");
    var hops = [
      { hop: "PC", header: "Builds an Ethernet frame carrying an IPv4 ICMP echo request", ports: "—", x: 55 },
      { hop: "Switch", header: "Forwards the frame by MAC address; adds a VLAN tag only on a trunk", ports: "—", x: 270 },
      { hop: "Router", header: "Routes by IPv4 address, lowers the TTL by 1, and builds a new frame", ports: "—", x: 430 },
      { hop: "Server", header: "Answers the echo request with an echo reply", ports: "—", x: 580 }
    ];
    document.getElementById("netSend").addEventListener("click", function () {
      body.textContent = "";
      packet.removeAttribute("hidden");
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
