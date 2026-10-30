# In-browser Linux VM assets (every `vm` lab and the VM stages of lab scenarios)

Everything is served from this LMS; no lab loads code from a third-party host. `ciwt-linux.bin` is committed. The
emulator and BIOS files are fetched by `tools/fetch_v86.sh` (pinned and sha256-checked) and are git-ignored.

| File | Project | Licence | Notes |
|---|---|---|---|
| libv86.js, v86.wasm | [v86](https://github.com/copy/v86) 0.5.471 (npm) | BSD-2-Clause (LICENSE.v86) | x86 emulator compiled to WebAssembly |
| seabios.bin | [SeaBIOS](https://www.seabios.org/) (from the v86 repo, rev 94faf3d) | LGPL-3.0 | unmodified binary; source at seabios.org |
| vgabios.bin | SeaVGABIOS / v86 repo | LGPL-3.0 | unmodified binary |
| **ciwt-linux.bin** / **novak-linux.bin** | Our build (`tools/vm_image/`): Linux 6.8.12 + BusyBox 1.36.1 + Alpine v3.20 x86 packages | GPL-2.0 kernel and BusyBox, plus the package licences below | terminal labs; see "GPL source offer" |
| **novak-gui.bin** + **novak-gui.state.gz** | Desktop guest (`tools/vm_gui/`, `docs/VM_GUI.md`): same base plus an X11 desktop | guest programs only; not linked into the LMS | see the desktop table |
| buildroot-bzImage68.bin | Upstream v86 image (fetched, no longer used by any lab) | GPL-2.0 and others | kept only for comparison |

Package licences in `ciwt-linux.bin` (exact versions are in `tools/vm_image/packages.txt` and `repo.txt`):

| Licence | Packages |
|---|---|
| GPL-2.0(-or-later) | Linux kernel, BusyBox, iptables, dnsmasq (GPL-2.0/3.0), apk-tools, e2fsprogs programs, iproute2 (`ss`), util-linux programs (lsblk, findmnt, mount, umount, blkid), socat |
| LGPL-2.1 | util-linux libraries (libblkid, libmount, libsmartcols, libuuid), libmnl, libnftnl, libxtables, e2fsprogs libraries |
| BSD / ISC / MIT-style | OpenSSH (BSD), sudo (ISC), shadow (BSD-3), linux-pam (BSD-3 or GPL), ldns/drill (BSD-3), libedit (BSD-3), libcap2 (BSD-3 or GPL-2), libbsd/libmd (BSD/ISC), skalibs/utmps (ISC), musl (MIT), ncurses (MIT-X11), libeconf (MIT), darkhttpd (ISC), tcpdump/libpcap (BSD-3), curl (curl licence) |
| Other permissive | OpenSSL 3 (Apache-2.0), zlib (Zlib), ca-certificates bundle (MPL-2.0) |

**GPL source offer.** The image contains GPL software, so whoever distributes it must offer the corresponding
source. This repository carries the full build recipe: `tools/vm_image/build.sh`, the kernel config additions, the
exact package list and the pinned source URLs with their checksums. The sources themselves are the pinned kernel.org
tarball, the upstream Buildroot/v86 sources and Alpine's aports at the listed package versions. Before serving the
image publicly, put a written offer, or a mirror of those source tarballs, next to the image (for example
`static/vendor/v86/SOURCES.txt` with a download link) and keep it for at least three years.

## Desktop guest (`novak-gui.bin`)

Used only by the Linux desktop labs. Every program below runs inside the virtual machine. None of them is linked
into the LMS process, the page's JavaScript, or a Python extension. The same GPL source offer covers the kernel
and BusyBox. Alpine package versions are the v3.20 x86 builds named in `docs/VM_GUI.md`.

| Component | Licence | Role |
|---|---|---|
| Linux 6.8.12 | GPL-2.0 | kernel, inside the guest image |
| BusyBox 1.36.1 | GPL-2.0 | shell and core utilities, separate binaries |
| X.Org server 21.1.14, xterm, xmessage, xset, bitmap fonts | MIT / X11 | display server, terminal, dialogs, fonts |
| Fluxbox 1.3.7 | MIT | window manager |
| FLTK 1.3.9 (`libfltk`) | LGPL-2.0 with the FLTK static-linking exception | widget library. **Flag:** LGPL, not a permissive licence. It is dynamically linked and used only inside the guest. The file manager, editor, and settings tool are Novak's own MIT code and are not combined into the LMS. |
| nfiles, nedit, nsettings, hog, novak-* | MIT (Novak LMS, `tools/vm_gui/src` and `tools/vm_gui/guest`) | desktop tools, guest-only |
| musl, fontconfig, libpng, libjpeg-turbo, pixman | MIT | libraries used by the programs above |
| FreeType | FTL (BSD-style) | fonts for xterm and FLTK |
| Mesa libGL / libEGL (pulled in by the X server package) | MIT | X.Org's GL dependency. No Gallium/LLVM drivers are in the image. The LMS does not link Mesa. |
| iptables, e2fsprogs, OpenSSH, sudo, shadow, apk-tools | same table as the terminal image | firewall, disks, SSH, accounts, packages |

`novak-gui.state.gz` is a memory snapshot of this guest after the desktop is up. It is data, not a separate program.
