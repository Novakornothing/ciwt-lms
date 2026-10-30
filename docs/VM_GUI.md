# Linux desktop image

The eight `linux-gui-*` labs boot this guest in v86. It is a real X11 desktop on the Bochs framebuffer
(`/dev/fb0` at 800×600), not a picture of one.

| | |
|---|---|
| Files | `static/vendor/v86/novak-gui.bin` (kernel + initramfs), `static/vendor/v86/novak-gui.state.gz` (saved v86 state) |
| Emulator | v86 0.5.471, BSD-2-Clause |
| Guest RAM | 192 MB, VGA memory 8 MB |
| Desktop | Fluxbox (MIT), Files / Editor / Settings (MIT, FLTK widgets), xterm (MIT) |
| Cold boot to the menu | about 6.5 s in Node on this build machine |
| Restore of the snapshot to a shell prompt | under 1 s once the snapshot is in memory |

The browser loads the gzip snapshot, restores it, and shows a progress bar while the bytes download.
Right-click the desktop for Terminal, Files, Editor, and Settings. Grading uses the same 9p probe as the
terminal labs (`labs_vm.py`). Stage 2 and 3 values are chosen per session and written into ticket files
inside the guest; the lab page does not contain them.

## Display caveat

Xorg, Fluxbox, the file manager, the editor, and the terminal all run inside the guest (confirmed with
`ps` and with the graders). The v86 canvas is resized to 800×600 when the VESA mode is set, but the
pixel buffer v86 scans does not receive the bytes X writes into `/dev/fb0`. A direct framebuffer
(`/dev/fb0` mapped at the Bochs linear framebuffer) and a SeaBIOS + `vga=0x314` boot were both tried.
`/dev/fb0` readback stays empty while Fluxbox is running, and forcing a full SVGA redraw in v86 stays
black. Grading does not depend on the canvas: it reads the guest through the serial shell and the 9p
probe. Until that copy path is fixed, a student does not see the windows on the canvas.

## What is questionable

FLTK is LGPL-2.0 with a linking exception. It is a shared library inside the guest only. The LMS does not
link it. The kernel, BusyBox, and iptables are GPL and likewise exist only as separate programs in the image.
The licence table is `static/vendor/v86/LICENSES.md`.

## Rebuilding

`tools/vm_gui/guest/` is the overlay (scripts, Fluxbox menu, init). `tools/vm_gui/src/` is the MIT desktop
tools, compiled with Alpine 3.20 i386 `g++` and `fltk-config`. The kernel is Linux 6.8.12 i386 with the
terminal image's config plus `CONFIG_DRM_BOCHS`, framebuffer console, and PS/2 mouse. The X server uses the
`fbdev` driver on `/dev/fb0`. Boot command line:

```
console=ttyS0,115200 tsc=reliable mitigations=off random.trust_cpu=on video=800x600
```

After the image reaches `NOVDESK_READY` on the serial port and the prompt returns, `save_state` from v86
0.5.471 is gzip-compressed to `novak-gui.state.gz`. A new snapshot has to be taken with the same v86 build,
the same RAM size, and the same VGA memory size.
