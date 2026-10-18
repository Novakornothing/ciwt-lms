#!/usr/bin/env bash
# Build the CIWT lab Linux image: static/vendor/v86/ciwt-linux.bin (one bzImage with an embedded initramfs).
#
#   kernel    Linux 6.8.12 with the upstream v86 Buildroot config (pinned, sha256) + linux.extra.config
#             (netfilter/nftables+iptables, loop, ATA disk, veth, bridge, VLAN, dummy, /proc/config.gz)
#   userland  the upstream v86 Buildroot rootfs (BusyBox 1.36, uClibc), trimmed (trim.txt), plus real Alpine
#             v3.20 x86 packages (packages.txt) installed with apk so `apk` works inside the VM, plus overlay/,
#             plus an offline signed package repository (repo.txt) for the package lab.
#
# Needs: sudo (for root-owned files: setuid sudo, /dev/console), make gcc bc flex bison libelf-dev cpio curl.
# Usage: tools/vm_image/build.sh [WORKDIR]      (default /tmp/ciwt-image; ~1.6 GB, ~15 min on 8 cores)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
W="${1:-/tmp/ciwt-image}"; mkdir -p "$W"; cd "$W"
OUT="$ROOT/static/vendor/v86/ciwt-linux.bin"
ALP=https://dl-cdn.alpinelinux.org/alpine/v3.20
KVER=6.8.12
fetch() { [ -f "$2" ] && echo "$3  $2" | sha256sum -c --quiet - 2>/dev/null && return; curl -fsSLo "$2" "$1"; echo "$3  $2" | sha256sum -c -; }

# 1. inputs (pinned)
fetch https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-$KVER.tar.xz linux-$KVER.tar.xz 19b31956d229b5b9ca5671fa1c74320179682a3d8d00fc86794114b21da86039
fetch https://gist.githubusercontent.com/SuperMaxusa/19a789c9e9b4a69b3237947fdb86d61e/raw/494e00ff0a2817dcf026072f30e7a217d6f4a372/.config-linux linux.config 34f23bbd3d1f8d45dc9a130f06c9cb53182740e66ffe350fbde4f7c343f663a2
UP="$ROOT/static/vendor/v86/buildroot-bzImage68.bin"
echo "507a759c70ab7a490a233be454d0b5b88bc667956a410b531cb4edc091e2eb1c  $UP" | sha256sum -c - || { echo "run tools/fetch_v86.sh first"; exit 1; }
fetch $ALP/main/x86_64/apk-tools-static-2.14.4-r1.apk apk-tools-static.apk "$(sed -n 's/^apk-tools-static //p' "$HERE/sha256.txt")"
fetch $ALP/main/x86/alpine-keys-2.4-r1.apk alpine-keys.apk "$(sed -n 's/^alpine-keys //p' "$HERE/sha256.txt")"
mkdir -p apkst ak; tar xzf apk-tools-static.apk -C apkst 2>/dev/null; tar xzf alpine-keys.apk -C ak 2>/dev/null
APK="$W/apkst/sbin/apk.static"

# 2. upstream rootfs out of the upstream bzImage (gzip kernel payload -> vmlinux -> gzip cpio)
python3 - "$UP" <<'PY'
import sys, zlib, re
b = open(sys.argv[1], 'rb').read()
v = zlib.decompressobj(16 + 15).decompress(b[b.find(b'\x1f\x8b\x08'):])
for m in re.finditer(rb'\x1f\x8b\x08', v):
    try:
        c = zlib.decompressobj(16 + 15).decompress(v[m.start():])
    except zlib.error:
        continue
    if c[:6] == b'070701' and len(c) > 1 << 20:
        open('upstream-rootfs.cpio', 'wb').write(c); break
else:
    sys.exit('initramfs not found')
PY
sudo rm -rf rootfs stage && mkdir rootfs stage
(cd rootfs && sudo cpio -idm --quiet < ../upstream-rootfs.cpio)
grep -v '^#' "$HERE/trim.txt" | while read -r p; do [ -n "$p" ] && sudo rm -rf "rootfs/$p"; done

# 3. Alpine packages, installed by apk into a staging root (real /lib/apk/db), exact versions
sudo mkdir -p stage/etc/apk && sudo cp -rL ak/usr/share/apk/keys/x86 stage/etc/apk/keys && echo x86 | sudo tee stage/etc/apk/arch >/dev/null
PKGS=$(grep -v '^#' "$HERE/packages.txt" | awk '{print $1"="$2}' | grep -vE '^(busybox|busybox-binsh|ssl_client)=')
sudo "$APK" --arch x86 --root "$W/stage" --initdb --no-scripts --no-cache -X $ALP/main -X $ALP/community add $PKGS >/dev/null
# BusyBox stays Buildroot's: keep Alpine's busybox packages registered (dependencies hold) but owning no files
sudo python3 - stage/lib/apk/db/installed <<'PY'
import sys
p = sys.argv[1]; out = []; skip = False
for blk in open(p).read().split('\n\n'):
    name = next((l[2:] for l in blk.splitlines() if l.startswith('P:')), '')
    if name in ('busybox', 'busybox-binsh'):
        blk = '\n'.join(l for l in blk.splitlines() if l[:2] not in ('F:', 'R:', 'a:', 'Z:', 'M:'))
    out.append(blk)
open(p, 'w').write('\n\n'.join(out))
PY
sudo rm -rf stage/var/cache stage/run stage/tmp stage/bin/busybox stage/bin/sh stage/etc/busybox-paths.d stage/etc/securetty stage/etc/network stage/etc/udhcpc stage/lib/apk/db/scripts.tar
sudo cp -a --remove-destination stage/. rootfs/
grep -v '^#' "$HERE/trim-alpine.txt" | while read -r p; do [ -n "$p" ] && sudo sh -c "rm -rf rootfs/$p"; done
KEEP=" $(grep -v '^#' "$HERE/xtables-keep.txt" | xargs) "
KEEPPAM=" $(grep -v '^#' "$HERE/pam-keep.txt" | xargs) "
for f in rootfs/lib/security/*.so; do case "$KEEPPAM" in *" ${f##*/} "*) ;; *) sudo rm -f "$f";; esac; done
for f in rootfs/usr/lib/xtables/*.so; do case "$KEEP" in *" ${f##*/} "*) ;; *) sudo rm -f "$f";; esac; done

# 4. offline package repository for the package lab, index signed with a throwaway build key
sudo mkdir -p rootfs/var/lib/ciwt-repo/x86 && mkdir -p repo
grep -v '^#' "$HERE/repo.txt" | while read -r n v r; do
  [ -f "repo/$n-$v.apk" ] || curl -fsSLo "repo/$n-$v.apk" "$ALP/$r/x86/$n-$v.apk"; done
[ -f ciwt-local.rsa ] || { openssl genrsa -out ciwt-local.rsa 2048 2>/dev/null; openssl rsa -in ciwt-local.rsa -pubout -out ciwt-local.rsa.pub 2>/dev/null; }
(cd repo && "$APK" index --allow-untrusted --rewrite-arch x86 -o APKINDEX.unsigned.tar.gz -d "CIWT offline lab repository" *.apk >/dev/null)
python3 - <<'PY'
import io, subprocess, tarfile, gzip
idx = open('repo/APKINDEX.unsigned.tar.gz', 'rb').read()
sig = subprocess.run(['openssl', 'dgst', '-sha1', '-sign', 'ciwt-local.rsa'], input=idx, capture_output=True, check=True).stdout
ti = tarfile.TarInfo('.SIGN.RSA.ciwt-local.rsa.pub'); ti.size = len(sig); ti.mode = 0o644
raw = ti.tobuf(tarfile.USTAR_FORMAT) + sig + b'\0' * (-len(sig) % 512)   # tar entry without end-of-archive (abuild-tar --cut)
open('repo/APKINDEX.tar.gz', 'wb').write(gzip.compress(raw, 9) + idx)
PY
sudo cp repo/*.apk repo/APKINDEX.tar.gz rootfs/var/lib/ciwt-repo/x86/
sudo cp ciwt-local.rsa.pub rootfs/etc/apk/keys/
echo /var/lib/ciwt-repo | sudo tee rootfs/etc/apk/repositories >/dev/null

# 5. overlay (users for sshd/dnsmasq, service helper, init scripts, real /var/log and /var/spool, release file)
sudo cp -a --remove-destination "$HERE/overlay/." rootfs/
sudo rm -f rootfs/var/log rootfs/var/spool; sudo mkdir -p rootfs/home rootfs/var/log rootfs/var/spool/cron/crontabs rootfs/var/empty rootfs/root/.ssh
sudo chmod 700 rootfs/root/.ssh; sudo chmod 1730 rootfs/var/spool/cron/crontabs
grep -q '^sshd:' rootfs/etc/passwd || { echo 'sshd:x:22:22:sshd privsep:/var/empty:/sbin/nologin' | sudo tee -a rootfs/etc/passwd >/dev/null; echo 'sshd:x:22:' | sudo tee -a rootfs/etc/group >/dev/null; echo 'sshd:*:::::::' | sudo tee -a rootfs/etc/shadow >/dev/null; }
grep -q '^dnsmasq:' rootfs/etc/passwd || { echo 'dnsmasq:x:100:101:dnsmasq:/dev/null:/sbin/nologin' | sudo tee -a rootfs/etc/passwd >/dev/null; echo 'dnsmasq:x:101:' | sudo tee -a rootfs/etc/group >/dev/null; echo 'dnsmasq:*:::::::' | sudo tee -a rootfs/etc/shadow >/dev/null; }
sudo chown -R 0:0 rootfs; sudo chmod 4755 rootfs/usr/bin/sudo; sudo chmod 0440 rootfs/etc/sudoers
(cd rootfs && sudo find . -print0 | sudo cpio --null -o -H newc --quiet) > initramfs-ciwt.cpio

# 6. kernel with the initramfs embedded
[ -d linux-$KVER ] || tar xf linux-$KVER.tar.xz
cd linux-$KVER
cp ../linux.config .config && cat "$HERE/linux.extra.config" >> .config
echo "CONFIG_INITRAMFS_SOURCE=\"$W/initramfs-ciwt.cpio\"" >> .config
make ARCH=i386 olddefconfig >/dev/null
make ARCH=i386 -j"$(nproc)" bzImage >/dev/null
cp arch/x86/boot/bzImage "$OUT"
cd "$W"
sha256sum "$OUT" | tee "$HERE/ciwt-linux.sha256"
ls -l "$OUT" | awk '{print "size", $5}'
