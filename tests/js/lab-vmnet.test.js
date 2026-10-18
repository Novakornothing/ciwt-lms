// Run: node --test tests/js/   — the real-VM labs' virtual network (switch, ARP, ping, DHCP, DNS) with synthetic frames.
const test = require('node:test');
const assert = require('node:assert');
const N = require('../../static/js/lab-vmnet.js');

const MAC = [0x00, 0x22, 0x15, 0x01, 0x02, 0x03];
const ip = (s) => s.split('.').map(Number);
function csum(b, o, l) { let s = 0; for (let i = 0; i < l - 1; i += 2) s += (b[o + i] << 8) | b[o + i + 1]; if (l & 1) s += b[o + l - 1] << 8; while (s >> 16) s = (s & 0xffff) + (s >> 16); return (~s) & 0xffff; }
function eth(dst, src, type, payload) { const f = new Uint8Array(14 + payload.length); f.set(dst, 0); f.set(src, 6); f[12] = type >> 8; f[13] = type & 255; f.set(payload, 14); return f; }
function ipv4(src, dst, proto, payload, ttl = 64) {
  const p = new Uint8Array(20 + payload.length); p[0] = 0x45; p[2] = p.length >> 8; p[3] = p.length & 255; p[8] = ttl; p[9] = proto;
  p.set(ip(src), 12); p.set(ip(dst), 16); const c = csum(p, 0, 20); p[10] = c >> 8; p[11] = c & 255; p.set(payload, 20); return p;
}
function udp(sp, dp, data) { const u = new Uint8Array(8 + data.length); u[0] = sp >> 8; u[1] = sp & 255; u[2] = dp >> 8; u[3] = dp & 255; u[4] = u.length >> 8; u[5] = u.length & 255; u.set(data, 8); return u; }
function arpReq(sha, spa, tpa) { const a = new Uint8Array(28); a.set([0, 1, 8, 0, 6, 4, 0, 1]); a.set(sha, 8); a.set(ip(spa), 14); a.set(ip(tpa), 24); return eth([255, 255, 255, 255, 255, 255], sha, 0x0806, a); }
function dhcp(type, xid, extra = []) {
  const b = new Uint8Array(300); b[0] = 1; b[1] = 1; b[2] = 6; b.set(xid, 4); b.set(MAC, 28); b.set([99, 130, 83, 99], 236);
  const o = [53, 1, type, ...extra, 255]; b.set(o, 240);
  return eth([255, 255, 255, 255, 255, 255], MAC, 0x0800, ipv4('0.0.0.0', '255.255.255.255', 17, udp(68, 67, b)));
}
function lan(cfg) {
  const fab = new N.Fabric(); const got = [];
  const port = fab.attach('ws', ['lan'], (f) => got.push(f));
  const svc = new N.Services(fab, cfg);
  return { fab, port, svc, got };
}
const CFG = { mac: '02:c1:77:00:00:01', ifaces: [{ seg: 'lan', ip: '10.10.0.1', bits: 24 }, { seg: 'lan', ip: '10.10.0.53', bits: 24 }],
  dhcp: { seg: 'lan', pool: ['10.10.0.100', '10.10.0.101'], router: '10.10.0.1', dns: '10.10.0.53', domain: 'ciwt.lab', bits: 24 },
  dns: { domain: 'ciwt.lab', records: { 'intranet.ciwt.lab': '10.10.0.80' } } };
const dhcpType = (f) => { for (let p = 14 + 20 + 8 + 240; p < f.length && f[p] !== 255; p += 2 + f[p + 1]) if (f[p] === 53) return f[p + 2]; return 0; };

test('DHCP: DISCOVER → OFFER, REQUEST → ACK with router, DNS and the same address', () => {
  const { port, svc, got } = lan(CFG);
  port.send(dhcp(1, [1, 2, 3, 4]));
  assert.strictEqual(got.length, 1); assert.strictEqual(dhcpType(got[0]), 2);
  const yi = Array.from(got[0].slice(14 + 28 + 16, 14 + 28 + 20)).join('.');
  assert.strictEqual(yi, '10.10.0.100');
  port.send(dhcp(3, [1, 2, 3, 4], [50, 4, ...ip(yi)]));
  assert.strictEqual(dhcpType(got[1]), 5);
  assert.deepStrictEqual(svc.events.map((e) => e.msg), ['DISCOVER', 'OFFER', 'REQUEST', 'ACK']);
  // asking for an address the server did not offer gets a NAK
  port.send(dhcp(3, [9, 9, 9, 9], [50, 4, 10, 10, 0, 7]));
  assert.strictEqual(dhcpType(got[2]), 6);
});

test('ARP reply and ping reply for the services addresses only', () => {
  const { port, got } = lan(CFG);
  port.send(arpReq(MAC, '10.10.0.100', '10.10.0.53'));
  assert.strictEqual(got.length, 1);
  assert.strictEqual(Array.from(got[0].slice(28, 32)).join('.'), '10.10.0.53');
  port.send(arpReq(MAC, '10.10.0.100', '10.10.0.99'));
  assert.strictEqual(got.length, 1, 'no reply for an address nobody owns');
  const echo = new Uint8Array([8, 0, 0, 0, 0, 1, 0, 1, 1, 2, 3, 4]); const c = csum(echo, 0, echo.length); echo[2] = c >> 8; echo[3] = c & 255;
  port.send(eth([2, 0xc1, 0x77, 0, 0, 1], MAC, 0x0800, ipv4('10.10.0.100', '10.10.0.1', 1, echo)));
  const r = got[got.length - 1];
  assert.strictEqual(r[14 + 20], 0, 'echo reply'); assert.strictEqual(csum(r, 14 + 20, r.length - 34), 0, 'valid ICMP checksum');
});

test('DNS: A record, NXDOMAIN, and the query is logged', () => {
  const { port, svc, got } = lan(CFG);
  port.send(arpReq(MAC, '10.10.0.100', '10.10.0.53'));      // services learns the client's MAC
  const q = (name) => { const parts = []; name.split('.').forEach((l) => { parts.push(l.length, ...Buffer.from(l)); }); return new Uint8Array([0, 7, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, ...parts, 0, 0, 1, 0, 1]); };
  port.send(eth([2, 0xc1, 0x77, 0, 0, 1], MAC, 0x0800, ipv4('10.10.0.100', '10.10.0.53', 17, udp(40000, 53, q('intranet.ciwt.lab')))));
  let r = got[got.length - 1]; const d = r.slice(14 + 20 + 8);
  assert.strictEqual(d[3] & 15, 0); assert.strictEqual(d[7], 1);
  assert.deepStrictEqual(Array.from(d.slice(d.length - 4)), [10, 10, 0, 80]);
  port.send(eth([2, 0xc1, 0x77, 0, 0, 1], MAC, 0x0800, ipv4('10.10.0.100', '10.10.0.53', 17, udp(40000, 53, q('nope.ciwt.lab')))));
  r = got[got.length - 1]; assert.strictEqual(r[14 + 20 + 8 + 3] & 15, 3);
  assert.ok(svc.events.some((e) => e.type === 'dns' && e.q === 'intranet.ciwt.lab' && e.rcode === 0));
});

test('switch isolates segments: a frame reaches only ports that share a segment', () => {
  const fab = new N.Fabric(); const a = [], b = [], r = [];
  const pa = fab.attach('pc', ['lan1'], (f) => a.push(f));
  fab.attach('srv', ['lan2'], (f) => b.push(f));
  fab.attach('rtr', ['lan1', 'lan2'], (f) => r.push(f));
  pa.send(arpReq(MAC, '10.1.0.10', '10.1.0.1'));
  assert.strictEqual(r.length, 1); assert.strictEqual(b.length, 0, 'LAN 2 never sees LAN 1 broadcasts');
  assert.ok(/ARP who has 10\.1\.0\.1\? tell 10\.1\.0\.10/.test(fab.log[0].s));
});
