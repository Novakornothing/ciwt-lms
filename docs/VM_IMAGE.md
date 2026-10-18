# The Linux image behind the real-VM labs

## What runs today (round 2, 18 Oct 2026)

| | |
|---|---|
| Emulator | v86 0.5.471 (x86 → WebAssembly), BSD-2-Clause |
| Firmware | SeaBIOS / SeaVGABIOS (LGPL-3.0) |
| Guest | **`static/vendor/v86/ciwt-linux.bin`: our own build**, made with `tools/vm_image/build.sh`. Linux 6.8.12-ciwt (gzip) with an embedded zstd initramfs: a trimmed BusyBox 1.36.1 rootfs plus real Alpine v3.20 x86 (musl) packages installed with `apk` |
| Image size | **10,781,184 bytes (10.8 MB)**. The upstream v86 Buildroot image was 10,068,480 bytes, so the extra tools cost 0.7 MB. |
| Total first download | **13.3 MB** (image 10.78 + v86.wasm 2.01 + libv86.js 0.36 + BIOSes 0.17), served by this LMS and cached by the browser |
| Committed? | Yes. `ciwt-linux.bin` is in git so a plain checkout works; `.gitignore` excludes only the fetched upstream files |
| Memory per VM | 80 MB guest RAM. v86 keeps 16 MB, and 64 MB is too small to unpack this initramfs. |
| Snapshot size | About 74 MB per VM (`save_state`), plus the blank disk for the disk lab (48 MB, sparse in practice) |

**Boot to a prompt, including the lab's setup script**:

| Where | 1 VM | 2 VMs |
|---|---|---|
| Node, headless (`tools/vm_headless.py`) | 2.6 s | — |
| Chromium, Playwright e2e, desktop 1280×900 | 3.9–4.8 s | 7.8–9.4 s |
| Chromium, phone profile 390×844 (no CPU throttle) | 3.4–4.6 s | 6.5–9.0 s |
| Chromium, tablet 820×1180 | 3.4–4.4 s | 6.5–8.8 s |

Throttled phone numbers (CPU ×4 / ×6) for the round-1 image are in `tools/vm_device_check.py`. The new image boots
in the same time to within 0.5 s, because the kernel is still gzip. XZ (5.2 s) and zstd kernels (4.1 s) were measured
and rejected.

## What is in the image

| Area | Real tools (versions) | Used by |
|---|---|---|
| Shell and core | BusyBox 1.36.1 (ash, coreutils, `vi`, `grep`, `sed`, `awk`, `find`, `ps`, `crond`, `syslogd`, `udhcpc`, `ip`, `ping`, `traceroute`, `nslookup`, `start-stop-daemon`) | every lab |
| Accounts | shadow 4.15 (`useradd`, `usermod`, `groupadd`, `gpasswd`, `chage`, `chpasswd`), linux-pam 1.6, **sudo 1.9.15** with `/etc/sudoers.d` and `visudo -c` | users |
| Remote access | **OpenSSH 9.7** (`ssh`, `sshd`, `ssh-keygen`, `ssh-copy-id`, `scp`, sftp); only an ed25519 host key, made on first start | ssh, firewall |
| Firewall | **iptables 1.8.10** (nf_tables backend; kernel netfilter with conntrack, NAT, LOG and REJECT). There is no `nft` binary. | firewall |
| DNS and DHCP | **dnsmasq 2.90** as a resolver, authoritative zone, forwarder and DHCP server; `drill` (ldns 1.8.3), which works like `dig` for the basics; BusyBox `nslookup` | dns, nettrouble |
| Packages | **apk-tools 2.14** with a signed offline repository at `/var/lib/ciwt-repo` (darkhttpd 1.16) | packages |
| Storage | ATA disk driver (`/dev/sda` from a blank in-browser disk), e2fsprogs 1.47 (`mkfs.ext4`, `e2fsck`), util-linux 2.40 (`lsblk`, `findmnt --verify`, `mount`/`umount` with `LABEL=`/`UUID=`, `blkid`), BusyBox `fdisk`, `mkswap`, `swapon` | disk |
| Network tools | `ss` (iproute2 6.9), tcpdump, socat, curl, `wget` | packages, firewall |
| Kernel extras over upstream | netfilter (nf_tables plus legacy iptables matches), loop, ATA_PIIX + SCSI disk, VETH, BRIDGE, 802.1Q VLAN, DUMMY, IKCONFIG (`/proc/config.gz`) | — |

There is no init system beyond `/etc/profile`. It mounts `fstab` (`mount -a`), brings up `lo`, and waits so the two
console shells do not race. Labs start the services they need (`syslogd`, `sshd`, `dnsmasq`, `crond`) in their setup
script, and each service has a SysV script in `/etc/init.d` plus a `service` helper. Logs come from BusyBox `syslogd`
in `/var/log/messages`; there is no journald. The BusyBox `tar` has no `-z`, so the labs pipe through `gzip`.

## Rebuilding it

`sudo tools/vm_image/build.sh [WORKDIR]` (default `/tmp/ciwt-image`). Every input is pinned and sha256-checked in
`tools/vm_image/sha256.txt`. The steps:

1. **Inputs.** Fetch the kernel tarball, the upstream v86 Buildroot config, apk-tools-static and alpine-keys.
2. **Rootfs.** Extract the upstream rootfs and apply `trim.txt`.
3. **Packages.** Install exactly the versions in `packages.txt` with `apk.static`, so `/lib/apk/db` is real.
   `trim-alpine.txt`, `pam-keep.txt` and `xtables-keep.txt` remove the parts the labs do not use.
4. **Offline repo.** Build `/var/lib/ciwt-repo` from `repo.txt`, signed with a throwaway key whose public half is in
   `/etc/apk/keys`.
5. **Overlay and build.** Copy in `overlay/` (profile, fstab, init scripts, sshd_config). Build the kernel with
   `linux.extra.config` on top of the upstream config, then write `ciwt-linux.sha256`.

After any rebuild, check the labs again:

- `python tools/vm_headless.py <lab>` for every `linux-vm-*` lab, with the solution (must complete) and with
  `--commands none` (must give only `boot`)
- `tools/labs_e2e.py --only '^(linux-vm-|scn-)' --views desktop,phone,tablet`

Licences and the GPL source offer are covered in `static/vendor/v86/LICENSES.md`.
