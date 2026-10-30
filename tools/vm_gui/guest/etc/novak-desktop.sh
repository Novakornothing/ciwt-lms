#!/bin/sh
# Bring up X and Fluxbox. Restarts if X exits.
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH HOME=/root DISPLAY=:0
i=0
while [ ! -e /dev/fb0 ] && [ "$i" -lt 50 ]; do
  usleep 100000 2>/dev/null || sleep 1
  i=$((i+1))
done
while true; do
  /etc/novak-xorg.sh
  if [ -S /tmp/.X11-unix/X0 ]; then
    kill $(pidof Xorg) 2>/dev/null || true
    sleep 1
  fi
  Xorg :0 -config /tmp/xorg.conf -nolisten tcp -noreset >/var/log/Xorg.log 2>&1 &
  i=0
  while [ ! -S /tmp/.X11-unix/X0 ] && [ "$i" -lt 40 ]; do
    usleep 100000 2>/dev/null || sleep 1
    i=$((i+1))
  done
  if [ -S /tmp/.X11-unix/X0 ]; then
    echo NOVDESK_READY > /dev/ttyS0
    fluxbox
  fi
  sleep 1
done
