# Linux desktop image

The eight `linux-gui-*` labs boot this guest in v86. It is a real X11 desktop on the Bochs framebuffer
(`/dev/fb0` at 800×600), not a picture of one.

| | |
|---|---|
| Files | `static/vendor/v86/novak-gui.state.0.part` … `.2.part`, `novak-gui.state.json` |
| Emulator | v86 0.5.471, BSD-2-Clause |
| Guest RAM | 192 MB, VGA memory 8 MB, 800×600×16 |
| Desktop | Fluxbox (MIT), Files / Editor / Settings (MIT, FLTK widgets), xterm (MIT) |
| Snapshot bytes | about 49 MB across three gzip pieces, each under 25 MiB |
| Restore to a shell prompt | under 1 s once the pieces are in memory |

The page downloads the pieces in order, shows a byte progress bar, and stores them in the browser
Cache API (`novak-desktop-v1`). A second visit reads the cache and does not hit the network for the
snapshot. Right-click the desktop for Terminal, Files, Editor, and Settings. Grading uses the same 9p
probe as the terminal labs (`labs_vm.py`). Stage 2 and 3 values are chosen per session and written into
ticket files inside the guest; the lab page does not contain them.

## Display

v86 scans the Bochs linear framebuffer at physical `0xE0000000`. That is not guest RAM, and
`read_memory` from JavaScript does not see it. Linux `vesafb` does, when the real-mode VESA setup has
already selected a mode the VGA device maps. A direct bzImage boot skips that setup, so the canvas stays
in text mode. The image that produced this snapshot is booted from SeaBIOS with `vga=0x314`
(800×600×16). X uses the `fbdev` driver, `ShadowFB` off, depth 16. Depth 24 makes `fbdev` reject the
mode. Gzip-compressed PCF fonts are not opened by this X server; the boot script expands them and
`xterm` falls back to the built-in `fixed` font. Fluxbox's own root fill returns BadMatch on this
16-bit screen, so `nbg` (MIT, libX11) paints the blue background after Fluxbox starts.

The snapshot is taken after that desktop is on the framebuffer. The boot CD is ejected before
`save_state`, because a synchronous CD image is copied into the state and the guest no longer reads it.
Restoring the snapshot does not need the CD.

## Hosting at no extra cost

The snapshot is three pieces (`novak-gui.state.0.part` about 21 MiB, `.1.part` about 19 MiB,
`.2.part` about 9 MiB). Each piece is a complete gzip of one slice of the raw state. The names are
not `.gz`, because a `.gz` name makes this app tell the browser to decompress the file, and a slice
of one gzip stream is not a gzip file of its own.

Cloudflare Workers static assets reject a single file over 25 MiB. These pieces are under that limit,
so the same files can be copied onto the novakornothing.com Worker (or any Cloudflare static route)
without repacking. Render's static bandwidth is the limit if they stay on the app host. The browser
cache means a student pays that bandwidth once per machine, not once per lab.

## What is questionable

FLTK is LGPL-2.0 with a linking exception. It is a shared library inside the guest only. The LMS does not
link it. The kernel, BusyBox, and iptables are GPL and likewise exist only as separate programs in the image.
The licence table is `static/vendor/v86/LICENSES.md`.

## Rebuilding

`tools/vm_gui/guest/` is the overlay (scripts, Fluxbox menu, init). `tools/vm_gui/src/` is the MIT desktop
tools, including `nbg.c`, compiled with Alpine 3.20 i386 against the guest's libX11 and FLTK. The kernel
is Linux 6.8.12 i386 with `CONFIG_FB_VESA` and a PS/2 mouse. It is booted by SeaBIOS from an ISO so the
real-mode `vga=0x314` setup runs. X uses `fbdev` on `/dev/fb0`.

```
vga=0x314 console=ttyS0,115200 tsc=reliable mitigations=off random.trust_cpu=on
```

After the desktop is visible, eject the CD, `save_state` from v86 0.5.471, gzip the result, and split it
into pieces under 20 MiB named in `novak-gui.state.json`. A new snapshot has to be taken with the same
v86 build, the same 192 MB RAM, and the same 8 MB VGA memory.
