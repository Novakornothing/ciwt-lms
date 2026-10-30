#!/bin/sh
# First boot of the Novak Linux desktop image. Serial shell comes up after this exits.
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH
[ -x /bin/stat ] || ln -sf busybox /bin/stat
mkdir -p /dev/pts /proc /sys /tmp /run /var/log /var/lib/novak /root /etc/novak
mount -t proc proc /proc 2>/dev/null || true
mount -t sysfs sysfs /sys 2>/dev/null || true
mount -t devpts devpts /dev/pts 2>/dev/null || true
mount -a 2>/dev/null || true
i=0
while [ ! -d /mnt ] || ! mountpoint -q /mnt; do
  mount -a 2>/dev/null || true
  i=$((i+1))
  [ "$i" -gt 20 ] && break
  usleep 50000 2>/dev/null || sleep 1
done
echo novak-lnx-01 > /etc/hostname
hostname novak-lnx-01 2>/dev/null || true
ip link set lo up 2>/dev/null || true
ip link add eth0 type dummy 2>/dev/null || true
ip link set eth0 up 2>/dev/null || true
echo 0 > /proc/sys/kernel/printk 2>/dev/null || true
mkdir -p /var/run /etc/ssh
if [ ! -s /etc/ssh/ssh_host_ed25519_key ]; then
  ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N '' -q
fi
for spec in data.img:8192 extra.img:4096 ticket.img:4096; do
  name=${spec%%:*}; kb=${spec##*:}
  img=/var/lib/novak/$name
  if [ ! -s "$img" ]; then
    dd if=/dev/zero of="$img" bs=1024 count="$kb" 2>/dev/null
    mkfs.ext4 -F -q "$img"
  fi
done
if [ ! -x /usr/local/bin/backup-verify.sh ]; then
  mkdir -p /usr/local/bin
  printf '%s\n' '#!/bin/sh' 'echo backup-verify ok' > /usr/local/bin/backup-verify.sh
  chmod 755 /usr/local/bin/backup-verify.sh
fi
[ -s /root/notes.txt ] || printf '%s\n' 'Novak Linux notes' > /root/notes.txt
# Desktop on the framebuffer. The serial shell stays free for grading.
/etc/novak-desktop.sh >/var/log/desktop.log 2>&1 &
: > /dev/.novak-boot-done
