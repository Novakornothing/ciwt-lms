#!/usr/bin/env bash
# Fetch the self-hosted assets for the in-browser Linux VM lab (linux-vm-perms) into static/vendor/v86/.
# Pinned versions + sha256; nothing is loaded from third-party hosts at lab time. Re-run is a no-op when present.
set -euo pipefail
cd "$(dirname "$0")/../static/vendor/v86"
V86_VER=0.5.471
BIOS_REV=94faf3d6b19ecabc53a4010aaa24252fa6a162e2
declare -A SHA=(
  [libv86.js]=1b41074f7a5604f528dac6842baf7afccd79d7370b97ea3241944c275b67bec1
  [v86.wasm]=2fc5609ae837fcbc77147155de6f1014677ecab5369f5584ebc670e9d56e6510
  [seabios.bin]=73e3f359102e3a9982c35fce98eb7cd08f18303ac7f1ba6ebfbe6cdc1c244d98
  [vgabios.bin]=a4bc0d80cc3ca028c73dafa8fee396b8d054ce87ebd8abfbd31b06b437607880
  [buildroot-bzImage68.bin]=507a759c70ab7a490a233be454d0b5b88bc667956a410b531cb4edc091e2eb1c
)
ok() { [ -f "$1" ] && echo "${SHA[$1]}  $1" | sha256sum -c --quiet - 2>/dev/null; }
if ! ok libv86.js || ! ok v86.wasm; then
  tmp=$(mktemp -d); curl -fsSL "https://registry.npmjs.org/v86/-/v86-${V86_VER}.tgz" | tar xz -C "$tmp"
  cp "$tmp/package/build/libv86.js" "$tmp/package/build/v86.wasm" .; cp "$tmp/package/LICENSE" LICENSE.v86; rm -rf "$tmp"
fi
ok seabios.bin || curl -fsSLo seabios.bin "https://raw.githubusercontent.com/copy/v86/${BIOS_REV}/bios/seabios.bin"
ok vgabios.bin || curl -fsSLo vgabios.bin "https://raw.githubusercontent.com/copy/v86/${BIOS_REV}/bios/vgabios.bin"
ok buildroot-bzImage68.bin || curl -fsSLo buildroot-bzImage68.bin "https://i.copy.sh/buildroot-bzImage68.bin"
for f in "${!SHA[@]}"; do echo "${SHA[$f]}  $f"; done | sha256sum -c -
