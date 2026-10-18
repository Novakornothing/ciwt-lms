/* Virtual network for the real-VM labs. Runs in the page (and in Node for tests); no server involved.
 *  - Fabric: an Ethernet switch with isolated segments. Every v86 VM's NIC is a port; a frame from a port reaches
 *    only ports that share a segment with it (MAC learning for unicast). A router VM sits on two segments.
 *  - Services: a small host on one or more segments that answers ARP and ping for its addresses, sends ICMP port
 *    unreachable (so traceroute ends), and runs a DHCP server and a DNS server. It replies through a gateway for
 *    off-subnet clients, so routed traffic really crosses the router VM.
 * The VMs' kernels do everything else (ARP, routing, forwarding, udhcpc, nslookup, ping, traceroute) for real. */
(function (root) {
  'use strict';
  var BCAST = [255, 255, 255, 255, 255, 255];
  function ip2a(s) { return s.split('.').map(Number); }
  function a2ip(a, o) { return a[o] + '.' + a[o + 1] + '.' + a[o + 2] + '.' + a[o + 3]; }
  function mac2s(a, o) { var r = []; for (var i = 0; i < 6; i++) r.push((a[o + i] | 256).toString(16).slice(1)); return r.join(':'); }
  function ipn(s) { var a = ip2a(s); return ((a[0] << 24) >>> 0) + (a[1] << 16) + (a[2] << 8) + a[3]; }
  function nip(n) { return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join('.'); }
  function sameNet(a, b, bits) { var m = bits ? (~0 << (32 - bits)) >>> 0 : 0; return ((ipn(a) & m) >>> 0) === ((ipn(b) & m) >>> 0); }
  function csum(buf, o, len) { var s = 0; for (var i = 0; i < len - 1; i += 2) s += (buf[o + i] << 8) | buf[o + i + 1]; if (len & 1) s += buf[o + len - 1] << 8; while (s >> 16) s = (s & 0xffff) + (s >> 16); return (~s) & 0xffff; }
  function isBcast(f) { return (f[0] & 1) === 1; }

  /* ------------------------------------------------------------ switch */
  function Fabric(opts) {
    this.ports = []; this.macs = {}; this.log = []; this.max = (opts && opts.max_log) || 400; this.onframe = null; this.count = 0;
  }
  Fabric.prototype.attach = function (name, segs, deliver) {
    var p = { name: name, segs: segs.slice(), deliver: deliver };
    this.ports.push(p);
    var fab = this;
    return { send: function (frame) { fab.forward(p, frame); } };
  };
  Fabric.prototype.common = function (a, b) { for (var i = 0; i < a.segs.length; i++) if (b.segs.indexOf(a.segs[i]) >= 0) return a.segs[i]; return null; };
  Fabric.prototype.forward = function (src, frame) {
    frame = frame instanceof Uint8Array ? frame : new Uint8Array(frame);
    if (frame.length < 14) return;
    this.count++;
    var smac = mac2s(frame, 6), dmac = mac2s(frame, 0);
    this.macs[smac] = src; if (!(frame[6] & 1)) src.mac = frame.slice(6, 12);
    var sum = summarize(frame);
    if (sum) { this.log.push({ n: this.count, from: src.name, s: sum }); if (this.log.length > this.max) this.log.shift(); if (this.onframe) this.onframe(this.log[this.log.length - 1]); }
    var known = !isBcast(frame) && this.macs[dmac];
    for (var i = 0; i < this.ports.length; i++) {
      var q = this.ports[i];
      if (q === src) continue;
      var seg = this.common(src, q);
      if (!seg) continue;
      if (known && known !== q) continue;
      // v86's ne2k model (0.5.471) drops every multicast frame unless the NIC is promiscuous, so IPv6 neighbour and
      // router discovery (ff02::1, ff02::2, solicited-node groups) would never arrive. Deliver multicast to a port
      // addressed to that port's own MAC (the guest kernel still filters by IPv6 group), like a NIC that accepts it.
      if (isBcast(frame) && dmac !== 'ff:ff:ff:ff:ff:ff' && q.mac) { var c = frame.slice(); c.set(q.mac, 0); q.deliver(c, seg); continue; }
      q.deliver(frame, seg);
    }
  };

  /* ------------------------------------------------------------ packet summary (the Packets panel) */
  function summarize(f) {
    var et = (f[12] << 8) | f[13];
    if (et === 0x0806) {
      var op = (f[20] << 8) | f[21];
      return op === 1 ? 'ARP who has ' + a2ip(f, 38) + '? tell ' + a2ip(f, 28) : 'ARP ' + a2ip(f, 28) + ' is at ' + mac2s(f, 22);
    }
    if (et === 0x86dd) return summarize6(f);
    if (et !== 0x0800) return null;
    var ihl = (f[14] & 15) * 4, pr = f[23], s = a2ip(f, 26), d = a2ip(f, 30), o = 14 + ihl, ttl = f[22];
    if (pr === 1) {
      var t = f[o], c = f[o + 1];
      var n = { 0: 'echo reply', 8: 'echo request', 3: c === 3 ? 'port unreachable' : (c === 1 ? 'host unreachable' : 'unreachable'), 11: 'time exceeded', 5: 'redirect' }[t] || ('type ' + t);
      return 'ICMP ' + s + ' → ' + d + ' ' + n + ' (ttl ' + ttl + ')';
    }
    if (pr === 17) {
      var sp = (f[o] << 8) | f[o + 1], dp = (f[o + 2] << 8) | f[o + 3];
      if (dp === 67 || dp === 68) { var mt = dhcpType(f, o + 8); return 'DHCP ' + ({ 1: 'DISCOVER', 2: 'OFFER', 3: 'REQUEST', 4: 'DECLINE', 5: 'ACK', 6: 'NAK', 7: 'RELEASE', 8: 'INFORM' }[mt] || '?') + ' ' + s + ' → ' + d; }
      if (dp === 53 || sp === 53) { var q = dnsName(f, o + 8 + 12); return 'DNS ' + (sp === 53 ? 'answer' : 'query') + ' ' + (q ? q.name : '') + ' ' + s + ' → ' + d; }
      return 'UDP ' + s + ':' + sp + ' → ' + d + ':' + dp + ' (ttl ' + ttl + ')';
    }
    if (pr === 6) return 'TCP ' + s + ' → ' + d + ':' + ((f[o + 2] << 8) | f[o + 3]);
    return 'IP ' + s + ' → ' + d + ' proto ' + pr;
  }
  // IPv6 (the IPv6 lab's router advertisements, neighbour discovery, ping -6): shown like tcpdump would name them.
  function a2ip6(f, o) {
    var w = [], i;
    for (i = 0; i < 8; i++) w.push(((f[o + 2 * i] << 8) | f[o + 2 * i + 1]).toString(16));
    var bs = -1, bl = 0, cs = -1, cl = 0;                     // longest run of zero words (length >= 2) becomes ::
    for (i = 0; i < 8; i++) {
      if (w[i] === '0') { if (cs < 0) cs = i; cl++; if (cl > bl) { bs = cs; bl = cl; } } else { cs = -1; cl = 0; }
    }
    if (bl < 2) return w.join(':');
    return w.slice(0, bs).join(':') + '::' + w.slice(bs + bl).join(':');
  }
  function summarize6(f) {
    if (f.length < 54) return 'IPv6 (short frame)';
    var nh = f[20], hl = f[21], s = a2ip6(f, 22), d = a2ip6(f, 38), o = 54, guard = 0;
    while ((nh === 0 || nh === 43 || nh === 60) && o + 2 <= f.length && guard++ < 4) { nh = f[o]; o += (f[o + 1] + 1) * 8; }  // hop-by-hop, routing, dest opts
    if (nh === 58 && o < f.length) {
      var t = f[o], tgt = o + 24 <= f.length ? a2ip6(f, o + 8) : '';
      if (t === 133) return 'ICMPv6 ' + s + ' → ' + d + ' router solicitation';
      if (t === 134) {
        var pfx = '', p = o + 16;                                 // options after the 16-byte RA header; type 3 = prefix
        while (p + 2 <= f.length && f[p + 1] > 0) { if (f[p] === 3 && p + 32 <= f.length) { pfx = ' prefix ' + a2ip6(f, p + 16) + '/' + f[p + 2]; break; } p += f[p + 1] * 8; }
        return 'ICMPv6 ' + s + ' → ' + d + ' router advertisement' + pfx;
      }
      if (t === 135) return 'ICMPv6 ' + s + ' → ' + d + ' neighbor solicitation, who has ' + tgt;
      if (t === 136) return 'ICMPv6 ' + s + ' → ' + d + ' neighbor advertisement, tgt is ' + tgt;
      var n6 = { 128: 'echo request', 129: 'echo reply', 1: 'destination unreachable', 2: 'packet too big', 3: 'time exceeded', 137: 'redirect', 143: 'multicast listener report v2' }[t] || ('type ' + t);
      return 'ICMPv6 ' + s + ' → ' + d + ' ' + n6 + ' (hlim ' + hl + ')';
    }
    if ((nh === 17 || nh === 6) && o + 4 <= f.length) {
      var sp = (f[o] << 8) | f[o + 1], dp = (f[o + 2] << 8) | f[o + 3];
      if (nh === 17 && (dp === 53 || sp === 53)) { var q = dnsName(f, o + 8 + 12); return 'DNS ' + (sp === 53 ? 'answer' : 'query') + ' ' + (q ? q.name : '') + ' ' + s + ' → ' + d; }
      if (nh === 17 && (dp === 547 || dp === 546)) return 'DHCPv6 ' + s + ' → ' + d;
      return (nh === 17 ? 'UDP ' : 'TCP ') + '[' + s + ']:' + sp + ' → [' + d + ']:' + dp;
    }
    return 'IPv6 ' + s + ' → ' + d + ' next header ' + nh;
  }
  function dhcpType(f, o) {
    var p = o + 240;
    while (p < f.length && f[p] !== 255) { if (f[p] === 0) { p++; continue; } if (f[p] === 53) return f[p + 2]; p += 2 + f[p + 1]; }
    return 0;
  }
  function dhcpOpts(f, o) {
    var r = {}, p = o + 240;
    while (p < f.length && f[p] !== 255) { if (f[p] === 0) { p++; continue; } r[f[p]] = f.slice(p + 2, p + 2 + f[p + 1]); p += 2 + f[p + 1]; }
    return r;
  }
  function dnsName(f, p) {
    var parts = [], guard = 0;
    while (p < f.length && f[p] && guard++ < 64) { var l = f[p]; if (l & 0xc0) return null; parts.push(String.fromCharCode.apply(null, f.slice(p + 1, p + 1 + l))); p += 1 + l; }
    return { name: parts.join('.').toLowerCase(), end: p + 1 };
  }

  /* ------------------------------------------------------------ services host */
  function Services(fabric, cfg) {
    var self = this;
    this.cfg = cfg; this.mac = (cfg.mac || '02:c1:77:00:00:01').split(':').map(function (h) { return parseInt(h, 16); });
    this.ifs = cfg.ifaces;                            // [{seg, ip, bits, gw}]
    this.arp = {}; this.pending = {}; this.events = []; this.leases = (cfg.state && cfg.state.leases) || {};
    this.ports = {};
    var segs = {};
    this.ifs.forEach(function (i) { segs[i.seg] = 1; });
    Object.keys(segs).forEach(function (seg) {
      self.ports[seg] = fabric.attach(cfg.name || 'services', [seg], function (frame, s) { self.rx(frame, s); });
    });
  }
  Services.prototype.ev = function (e) { e.t = Date.now(); this.events.push(e); if (this.events.length > 200) this.events.shift(); };
  Services.prototype.ifFor = function (seg, ip) { for (var i = 0; i < this.ifs.length; i++) { var f = this.ifs[i]; if (f.seg === seg && (!ip || f.ip === ip)) return f; } return null; };
  Services.prototype.mine = function (seg, ip) { return this.ifs.some(function (f) { return f.seg === seg && f.ip === ip; }); };
  Services.prototype.tx = function (seg, frame) { this.ports[seg].send(frame); };
  Services.prototype.eth = function (dst, type, payload) {
    var f = new Uint8Array(14 + payload.length);
    f.set(dst, 0); f.set(this.mac, 6); f[12] = type >> 8; f[13] = type & 255; f.set(payload, 14);
    return f;
  };
  Services.prototype.rx = function (f, seg) {
    var et = (f[12] << 8) | f[13];
    if (et === 0x0806) return this.rxArp(f, seg);
    if (et !== 0x0800) return;
    var dmac = mac2s(f, 0);
    if (!isBcast(f) && dmac !== mac2s(this.mac, 0)) return;
    var ihl = (f[14] & 15) * 4, pr = f[23], src = a2ip(f, 26), dst = a2ip(f, 30), o = 14 + ihl;
    var ttl = f[22];
    if (pr === 17) {
      var dp = (f[o + 2] << 8) | f[o + 3];
      if (dp === 67 && this.cfg.dhcp && this.cfg.dhcp.seg === seg) return this.rxDhcp(f, o + 8, seg);
    }
    // cfg.remote: addresses "behind" this host acting as a router one hop away (it decrements TTL like a real router)
    var rem = (this.cfg.remote || []).filter(function (r) { return r.ip === dst; })[0];
    if (!rem && !this.mine(seg, dst)) return;
    this.arp[src] = this.arp[src] || mac2s(f, 6);
    if (rem && ttl <= 1) {                                        // TTL expires at this "router": ICMP time exceeded
      var me = this.ifFor(seg).ip;
      this.ev({ type: 'ttl', from: src, to: dst, at: me });
      return this.sendIp(seg, me, src, this.ipPacket(me, src, 1, concat([11, 0, 0, 0, 0, 0, 0, 0], f.slice(14, Math.min(f.length, o + 8))), true));
    }
    if (pr === 1 && f[o] === 8) {                                 // echo request -> reply
      var ip = f.slice(14, 14 + ((f[16] << 8) | f[17]));
      var r = new Uint8Array(ip);
      r.set(f.slice(30, 34), 12); r.set(f.slice(26, 30), 16); r[8] = rem ? 63 : 64; r[10] = r[11] = 0;
      var c = csum(r, 0, ihl); r[10] = c >> 8; r[11] = c & 255;
      r[ihl] = 0; r[ihl + 2] = r[ihl + 3] = 0; c = csum(r, ihl, r.length - ihl); r[ihl + 2] = c >> 8; r[ihl + 3] = c & 255;
      this.ev({ type: 'ping', from: src, to: dst, ttl: ttl });
      return this.sendIp(seg, rem ? this.ifFor(seg).ip : dst, src, r);
    }
    if (pr === 17) {
      var sp = (f[o] << 8) | f[o + 1], dport = (f[o + 2] << 8) | f[o + 3];
      if (dport === 53 && this.cfg.dns) return this.rxDns(f, o, seg, src, dst, sp);
      // closed port -> ICMP port unreachable (this is how traceroute knows it arrived)
      this.ev({ type: 'udp', from: src, to: dst, port: dport, ttl: ttl });
      var orig = f.slice(14, Math.min(f.length, o + 8));
      return this.sendIp(seg, rem ? this.ifFor(seg).ip : dst, src, this.ipPacket(dst, src, 1, concat([3, 3, 0, 0, 0, 0, 0, 0], orig), true));
    }
  };
  function concat(a, b) { var r = new Uint8Array(a.length + b.length); r.set(a, 0); r.set(b, a.length); return r; }
  Services.prototype.ipPacket = function (src, dst, proto, payload, icmp) {
    var p = new Uint8Array(20 + payload.length);
    p[0] = 0x45; p[2] = p.length >> 8; p[3] = p.length & 255; p[4] = (Math.random() * 255) | 0; p[6] = 0x40; p[8] = 64; p[9] = proto;
    p.set(ip2a(src), 12); p.set(ip2a(dst), 16);
    var c = csum(p, 0, 20); p[10] = c >> 8; p[11] = c & 255;
    p.set(payload, 20);
    if (icmp) { p[22] = p[23] = 0; c = csum(p, 20, payload.length); p[22] = c >> 8; p[23] = c & 255; }
    return p;
  };
  Services.prototype.udpPacket = function (src, dst, sp, dp, data) {
    var u = new Uint8Array(8 + data.length);
    u[0] = sp >> 8; u[1] = sp & 255; u[2] = dp >> 8; u[3] = dp & 255; u[4] = u.length >> 8; u[5] = u.length & 255; // checksum 0 = none (IPv4)
    u.set(data, 8);
    return this.ipPacket(src, dst, 17, u);
  };
  /* send an IP packet: on-link -> ARP the destination; off-link -> through this interface's gateway */
  Services.prototype.sendIp = function (seg, src, dst, pkt) {
    var itf = this.ifFor(seg, src) || this.ifFor(seg);
    var hop = sameNet(src, dst, itf.bits) ? dst : itf.gw;
    if (!hop) return this.ev({ type: 'drop', why: 'no route to ' + dst + ' (no gateway)' });
    var mac = this.arp[hop];
    if (mac) return this.tx(seg, this.eth(mac.split(':').map(function (h) { return parseInt(h, 16); }), 0x0800, pkt));
    (this.pending[hop] = this.pending[hop] || []).push([seg, pkt]);
    this.arpRequest(seg, itf.ip, hop);
  };
  Services.prototype.arpRequest = function (seg, sip, tip) {
    var a = new Uint8Array(28);
    a.set([0, 1, 8, 0, 6, 4, 0, 1], 0); a.set(this.mac, 8); a.set(ip2a(sip), 14); a.set(ip2a(tip), 24);
    this.tx(seg, this.eth(BCAST, 0x0806, a));
  };
  Services.prototype.rxArp = function (f, seg) {
    var op = (f[20] << 8) | f[21], spa = a2ip(f, 28), tpa = a2ip(f, 38), sha = mac2s(f, 22);
    if (spa !== '0.0.0.0' && (this.mine(seg, tpa) || this.arp[spa] || this.pending[spa])) this.arp[spa] = sha;
    if (op === 1 && this.mine(seg, tpa)) {
      var a = new Uint8Array(28);
      a.set([0, 1, 8, 0, 6, 4, 0, 2], 0); a.set(this.mac, 8); a.set(ip2a(tpa), 14); a.set(f.slice(22, 28), 18); a.set(ip2a(spa), 24);
      this.tx(seg, this.eth(f.slice(22, 28), 0x0806, a));
    }
    var q = this.pending[spa];
    if (q && this.arp[spa]) { delete this.pending[spa]; var self = this; q.forEach(function (x) { self.sendIp(x[0], a2ip(x[1], 12), a2ip(x[1], 16), x[1]); }); }
  };

  /* DHCP server (RFC 2131 subset: DISCOVER/OFFER, REQUEST/ACK|NAK, RELEASE) */
  Services.prototype.rxDhcp = function (f, o, seg) {
    var d = this.cfg.dhcp, opts = dhcpOpts(f, o), mt = opts[53] ? opts[53][0] : 0, mac = mac2s(f, o + 28);
    var xid = f.slice(o + 4, o + 8), flags = f.slice(o + 10, o + 12);
    var lease = this.leases[mac];
    if (!lease) {
      var used = {}, self = this;
      Object.keys(this.leases).forEach(function (k) { used[self.leases[k]] = 1; });
      for (var n = ipn(d.pool[0]); n <= ipn(d.pool[1]); n++) if (!used[nip(n)]) { lease = nip(n); break; }
      if (!lease) return this.ev({ type: 'dhcp', msg: 'NOPOOL', mac: mac });
    }
    var reply;
    if (mt === 1) { reply = 2; this.leases[mac] = lease; this.ev({ type: 'dhcp', msg: 'DISCOVER', mac: mac }); }
    else if (mt === 3) {
      var want = opts[50] ? a2ip(opts[50], 0) : a2ip(f, o + 12);
      this.ev({ type: 'dhcp', msg: 'REQUEST', mac: mac, ip: want });
      if (want !== lease && want !== '0.0.0.0') { reply = 6; } else { reply = 5; this.leases[mac] = lease; }
    } else if (mt === 7) { this.ev({ type: 'dhcp', msg: 'RELEASE', mac: mac, ip: lease }); delete this.leases[mac]; return; }
    else return;
    var srv = this.ifFor(seg).ip;
    var b = new Uint8Array(300); b[0] = 2; b[1] = 1; b[2] = 6; b.set(xid, 4); b.set(flags, 10);
    if (reply !== 6) b.set(ip2a(lease), 16);
    b.set(ip2a(srv), 20); b.set(f.slice(o + 28, o + 44), 28); b.set([99, 130, 83, 99], 236);
    var p = 240;
    function opt(code, bytes) { b[p++] = code; b[p++] = bytes.length; for (var i = 0; i < bytes.length; i++) b[p++] = bytes[i]; }
    opt(53, [reply]); opt(54, ip2a(srv));
    if (reply !== 6) {
      var bits = d.bits || 24, m = (~0 << (32 - bits)) >>> 0;
      opt(51, [0, 0, (d.lease_s || 3600) >> 8 & 255, (d.lease_s || 3600) & 255]); opt(1, ip2a(nip(m)));
      if (d.router) opt(3, ip2a(d.router));
      if (d.dns) opt(6, ip2a(d.dns));
      if (d.domain) opt(15, Array.prototype.map.call(d.domain, function (c) { return c.charCodeAt(0); }));
    }
    b[p++] = 255;
    var pkt = this.udpPacket(srv, '255.255.255.255', 67, 68, b.slice(0, Math.max(p, 300)));
    this.ev({ type: 'dhcp', msg: { 2: 'OFFER', 5: 'ACK', 6: 'NAK' }[reply], mac: mac, ip: lease });
    this.tx(seg, this.eth(BCAST, 0x0800, pkt));
  };

  /* DNS server: A records from cfg.dns.records, NXDOMAIN otherwise; PTR for the records' addresses */
  Services.prototype.rxDns = function (f, o, seg, src, dst, sp) {
    var q = f.slice(o + 8, o + ((f[o + 4] << 8) | f[o + 5]));
    if (q.length < 17) return;
    var name = dnsName(q, 12); if (!name) return;
    var qtype = (q[name.end] << 8) | q[name.end + 1];
    var recs = this.cfg.dns.records || {}, ans = [], rcode = 0, nm = name.name.replace(/\.$/, '');
    var fq = recs[nm] ? nm : (this.cfg.dns.domain && recs[nm + '.' + this.cfg.dns.domain] ? nm + '.' + this.cfg.dns.domain : null);
    if (qtype === 1 && fq) ans.push({ t: 1, d: ip2a(recs[fq]) });
    else if (qtype === 12 && /\.in-addr\.arpa$/.test(nm)) {
      var ip = nm.replace(/\.in-addr\.arpa$/, '').split('.').reverse().join('.');
      var host = Object.keys(recs).filter(function (k) { return recs[k] === ip; })[0];
      if (host) { var lab = []; host.split('.').forEach(function (s) { lab.push(s.length); for (var i = 0; i < s.length; i++) lab.push(s.charCodeAt(i)); }); lab.push(0); ans.push({ t: 12, d: lab }); }
      else rcode = 3;
    } else if (!fq) rcode = 3;
    this.ev({ type: 'dns', from: src, q: nm, qtype: qtype, rcode: rcode, answer: ans.length && qtype === 1 ? recs[fq] : null });
    var qs = q.slice(12, name.end + 4);
    var out = [q[0], q[1], 0x81, 0x80 | rcode, 0, 1, 0, ans.length, 0, 0, 0, 0];
    out = out.concat(Array.prototype.slice.call(qs));
    ans.forEach(function (a) { out = out.concat([0xc0, 12, 0, a.t, 0, 1, 0, 0, 0, 60, a.d.length >> 8, a.d.length & 255]).concat(a.d); });
    this.sendIp(seg, dst, src, this.udpPacket(dst, src, 53, sp, new Uint8Array(out)));
  };
  Services.prototype.snapshot = function () { return { leases: this.leases }; };

  var api = { Fabric: Fabric, Services: Services, summarize: summarize };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.VMNet = api;
})(typeof window !== 'undefined' ? window : globalThis);
