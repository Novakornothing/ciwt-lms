# The Linux image behind the real-VM labs

## What runs today

| | |
|---|---|
| Emulator | v86 0.5.471 (x86 → WebAssembly), BSD-2-Clause |
| Firmware | SeaBIOS / SeaVGABIOS (LGPL-3.0) |
| Guest | `buildroot-bzImage68.bin` — Linux 6.8.12, BusyBox 1.36.1, 9p share at `/mnt`, ne2k NIC driver, ~10 MB |
| Where it comes from | `tools/fetch_v86.sh` downloads the pinned files once, checks the sha256 and puts them in `static/vendor/v86/`. Students download them **from this LMS**; no lab loads code from a third-party host. Binaries are git-ignored. |
| Memory per VM | 64 MB guest RAM (48 MB does not boot this kernel). About 150 MB of browser memory per VM in total. |
| Snapshot size | About 43 MB per VM (`save_state`). Save, Resume and the instant Reset use it. |

**Measured boot to a prompt, including scenario setup** (Playwright, Chromium; `tools/vm_device_check.py`):

| Device class | 1 VM | 2 VMs (routing lab) | Resume from save | Reset from the clean snapshot |
|---|---|---|---|---|
| Laptop (no throttle) | 2.7–3.8 s | 5.1–6.1 s | 1–2 s | 0.1–0.2 s |
| Mid-range phone (CPU ×4, 390×844) | 8.6–9.1 s | 15.2–15.9 s | 0.9 s | 0.4–0.6 s |
| Older phone (CPU ×6) | 15.1 s | 25.3 s | 0.7–1.1 s | 0.7–0.8 s |

Phones that report under 4 GB of memory do not keep the clean snapshot for the two-VM lab, so there Reset is a cold boot.
If the boot takes over 45 s, or the device reports under 2 GB, the page offers the simulated version of the same lab.

## What this image can and cannot do

**What it can do.** BusyBox gives the labs:

- files, users, permissions, `find`, `grep`, `sed`, `awk`, `vi`, `less`, `top`
- `ps`, `kill`, `fuser`, `lsof`
- `crond` and `crontab`, `syslogd` and `logger`
- `start-stop-daemon` with init scripts
- `ip` (addr, route, neigh, link), `sysctl`, `ping`, `traceroute`, `arp`
- `udhcpc`, `nslookup`, `dnsd`, `wget`, `telnet` and `tftp`

**What it cannot do.** The kernel has no netns, veth, bridge, 802.1Q VLAN or netfilter. Each VM has one NIC.
These were tested in the guest and give `RTNETLINK answers: Operation not supported`. So the labs build networks
*between* VMs: `static/js/lab-vmnet.js` wires the VMs' NICs to an isolating switch, and adds a services host for
DHCP, DNS, ping and traceroute replies.

## An institution-owned image (recommended before wide use)

There are two reasons to build your own image:

1. **The GPL source obligation.** You must offer the exact source and config of the image you serve. With your
   own build, you publish the Buildroot `.config` and the `make legal-info` output next to the image.
2. **Richer networking in one VM.** Real namespaces, bridges, VLAN sub-interfaces, nftables and dnsmasq. With
   these, the routing lab could use a true router-on-a-stick and the services could be real daemons.

Recipe (Buildroot 2024.02 LTS or later, i386; follow v86's `docs/linux-9p-image.md` for the 9p and serial bits):

```
BR2_x86_i686=y
BR2_TARGET_ROOTFS_INITRAMFS=y            # kernel with embedded initramfs, one file like today
BR2_LINUX_KERNEL=y  BR2_LINUX_KERNEL_CUSTOM_CONFIG_FILE="board/ciwt/linux.config"
BR2_PACKAGE_BUSYBOX=y
BR2_PACKAGE_IPROUTE2=y BR2_PACKAGE_DNSMASQ=y BR2_PACKAGE_NFTABLES=y BR2_PACKAGE_TCPDUMP=y BR2_PACKAGE_NANO=y
# linux.config additions on top of v86's:
CONFIG_NET_NS=y CONFIG_VETH=y CONFIG_BRIDGE=y CONFIG_VLAN_8021Q=y CONFIG_NETFILTER=y CONFIG_NF_TABLES=y
CONFIG_NFT_NAT=y CONFIG_NF_CONNTRACK=y CONFIG_DUMMY=y CONFIG_NE2000=y CONFIG_NET_9P=y CONFIG_9P_FS=y
```

Install steps:

1. Build the image with `make`. Then run `make legal-info` and publish its output.
2. Copy `output/images/bzImage` to `static/vendor/v86/ciwt-bzImage.bin`.
3. Add its sha256 to `tools/fetch_v86.sh`.
4. Set `IMAGE["image"]` and `IMAGE["download_mb"]` in `labs_vm.py`.

The image will be larger, roughly 14–18 MB, and it needs a re-test. Run `python tools/vm_headless.py <lab>` for each
lab, then `tools/labs_e2e.py --only '^linux-vm-'` and `tools/vm_device_check.py`.
