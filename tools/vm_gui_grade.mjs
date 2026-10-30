// Boot the GUI desktop from its v86 snapshot, run setup + commands, print the probe text.
import fs from "fs";
import zlib from "zlib";
import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { V86 } = require(ROOT + "/static/vendor/v86/libv86.js");
const D = ROOT + "/static/vendor/v86";
const spec = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const manifest = JSON.parse(fs.readFileSync(D + "/novak-gui.state.json", "utf8"));
const raw = Buffer.concat(manifest.parts.map((p) => zlib.gunzipSync(fs.readFileSync(D + "/" + p))));
const buf = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
const e = new V86({
  wasm_path: D + "/v86.wasm",
  memory_size: (spec.memory_mb || 192) << 20,
  vga_memory_size: (spec.vga_mb || 8) << 20,
  bios: { url: D + "/seabios.bin" },
  vga_bios: { url: D + "/vgabios.bin" },
  initial_state: { buffer: buf },
  autostart: true, disable_keyboard: true, disable_mouse: true, disable_speaker: true, filesystem: {},
});
let out = "";
e.add_listener("serial0-output-byte", b => { out += String.fromCharCode(b); if (out.length > 20000) out = out.slice(-8000); });
const wait = (re, ms) => new Promise((res, rej) => {
  const st = Date.now();
  let quiet = 0;
  const iv = setInterval(() => {
    const lines = out.split("\n");
    const last = lines[lines.length - 1];
    if (re.test(last)) {
      quiet += 30;
      if (quiet >= 120) { clearInterval(iv); res(); }
    } else quiet = 0;
    if (Date.now() - st > ms) { clearInterval(iv); rej(new Error("timeout " + JSON.stringify(out.slice(-300)))); }
  }, 30);
});
await new Promise(r => e.add_listener("emulator-loaded", r));
const t0 = Date.now();
e.serial0_send("\n");
await wait(/[#%$] $/, 20000);
console.error("restore prompt", Date.now() - t0, "ms");
async function run(c, ms = 30000) {
  out = "";
  e.serial0_send(c + "\n");
  await wait(/[#%$] $/, ms);
  return out.split("\n").slice(1, -1).join("\n");
}
if (spec.setup) {
  await e.create_file("/.novak-setup", new TextEncoder().encode(spec.setup));
  const t = await run(" . /mnt/.novak-setup; rm -f /mnt/.novak-setup", 60000);
  if (t.trim()) console.error("[setup]", t.slice(0, 500));
}
for (const line of spec.commands || []) {
  const t = await run(line, 60000);
  if (spec.verbose) console.error("$ " + line + "\n" + t.slice(0, 400));
}
await e.create_file("/.ciwt-probe", new TextEncoder().encode(spec.probe));
await run(" sh /mnt/.ciwt-probe; rm -f /mnt/.ciwt-probe", 60000);
const result = new TextDecoder().decode(await e.read_file("/.ciwt-result"));
console.log(JSON.stringify({ probe: result, restore_ms: Date.now() - t0 }));
process.exit(0);
