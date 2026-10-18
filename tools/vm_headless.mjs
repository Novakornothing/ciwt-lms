// tools/vm_headless.py drives this: boots the lab machines in Node (v86), sources the setup, runs commands, runs the probes.
// Runs a lab's real scenario headless: boot machines, source setup, run solution commands, run probes. JSON in/out.
import fs from "fs"; import path from "path"; import { fileURLToPath } from "url"; import { createRequire } from "module";
const require = createRequire(import.meta.url); const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), ".."); const N = require(ROOT + "/static/js/lab-vmnet.js"); const { V86 } = require(ROOT + "/static/vendor/v86/libv86.js");
const D = ROOT + "/static/vendor/v86";
const spec = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const fab = new N.Fabric(); const vms = {}; const first = spec.vm.machines[0].name; const net = spec.vm.net;
for (const m of spec.vm.machines) {
  const e = new V86({ wasm_path: D + "/v86.wasm", memory_size: (m.memory_mb||80) << 20, hda: m.disk_mb ? { buffer: new ArrayBuffer(m.disk_mb << 20) } : undefined, vga_memory_size: 2 << 20,
    bios: { url: D + "/seabios.bin" }, vga_bios: { url: D + "/vgabios.bin" }, bzimage: { url: D + "/" + (spec.vm.image || "ciwt-linux.bin") },
    cmdline: "tsc=reliable mitigations=off random.trust_cpu=on", autostart: true, disable_keyboard: true, disable_mouse: true, disable_speaker: true, filesystem: {},
    net_device: net ? { type: "ne2k" } : undefined });
  const o = { e, out: "", name: m.name }; vms[m.name] = o;
  e.add_listener("serial0-output-byte", b => { o.out += String.fromCharCode(b); });
  if (net) { const port = fab.attach(m.label, m.segs, fr => e.bus.send("net0-receive", fr)); e.add_listener("net0-send", d => port.send(new Uint8Array(d))); }
}
const svc = net && net.services ? new N.Services(fab, net.services) : null;
let step = "boot";   // what we are waiting for, so a timeout says which step stalled (pass 17: a one-off firewall timeout in a full suite could not be placed)
const wait = (o, re, ms=+(process.env.VM_WAIT_MS||150000)) => new Promise((res, rej) => { const st = Date.now(); const iv = setInterval(() => { if (re.test(o.out)) { clearInterval(iv); res(); } else if (Date.now() - st > ms) { clearInterval(iv); rej(new Error(`timeout after ${ms} ms waiting on [${o.name}] ${step}; console tail: ${JSON.stringify(o.out.slice(-300))}`)); } }, 20); });
const P = /(\n[^\n]*[#%$] |assword: ?|\(yes\/no[^)]*\)\? ?)$/;   // shell prompt, or a password / host-key question
async function run(o, c, quiet) { step = "command " + JSON.stringify(c.slice(0, 120)); o.out = ""; o.e.serial0_send(c + "\n"); await wait(o, P); const t = o.out.split("\n").slice(1, -1).join("\n"); if (!quiet) console.error(`$ ${c}\n${t}`); return t; }
const T0 = Date.now();
await Promise.all(Object.values(vms).map(o => wait(o, /[#%$] $/)));
console.error(`[boot] ${Date.now() - T0} ms`);
for (const [name, o] of Object.entries(vms)) {
  const s = (spec.vm.setup || {})[name]; if (!s) continue;
  await o.e.create_file("/.ciwt-setup", new TextEncoder().encode(s));
  const t = await run(o, " . /mnt/.ciwt-setup; rm -f /mnt/.ciwt-setup", true);
  if (t.trim()) console.error(`[setup ${name}]`, t.slice(0, 400));
}
for (const line of spec.commands) { const m = line.match(/^\[(\w+)\] (.*)$/); const name = m ? m[1] : first; await run(vms[name], m ? m[2] : line, !spec.verbose); }
const out = { probes: {}, events: svc ? svc.events : [] };
for (const [name, o] of Object.entries(vms)) {
  await o.e.create_file("/.ciwt-probe", new TextEncoder().encode(spec.probes[name]));
  const t0 = Date.now();
  await run(o, " sh /mnt/.ciwt-probe; rm -f /mnt/.ciwt-probe", true);
  out.probes[name] = new TextDecoder().decode(await o.e.read_file("/.ciwt-result"));
  console.error(`[probe ${name}] ${Date.now() - t0} ms`);
}
console.log(JSON.stringify(out));
process.exit(0);
