# In-browser Linux VM assets (all `vm` labs: linux-vm-perms, linux-vm-shell, linux-vm-services, linux-vm-netclient, linux-vm-routing)

Fetched by `tools/fetch_v86.sh` (pinned, sha256-checked) and served from this LMS — the lab never loads code
from a third-party host. Binaries are not committed to git (see `.gitignore`).

| File | Project | Licence | Notes |
|---|---|---|---|
| libv86.js, v86.wasm | [v86](https://github.com/copy/v86) 0.5.471 (npm) | BSD-2-Clause (LICENSE.v86) | x86 emulator compiled to WebAssembly |
| seabios.bin | [SeaBIOS](https://www.seabios.org/) (from the v86 repo, rev 94faf3d) | LGPL-3.0 | unmodified binary; source at seabios.org |
| vgabios.bin | [SeaVGABIOS](https://www.seabios.org/) / v86 repo | LGPL-3.0 | unmodified binary |
| buildroot-bzImage68.bin | Linux 6.8.12 + BusyBox 1.36.1 initramfs, built with [Buildroot](https://buildroot.org) by the v86 author (i.copy.sh) | GPL-2.0 (kernel, BusyBox) plus the licences of the other Buildroot packages | **Distributing this image obliges you to offer the corresponding source.** For production, build your own image with Buildroot (v86 docs: docs/linux-9p-image.md, or github.com/Darin755/browser-buildroot) and publish its source tarball + config next to it. |

Licensing summary: the emulator is permissive (BSD-2); the guest OS is GPL — fine to serve, but you must offer the
source of the exact image you serve (written offer or a download link).
