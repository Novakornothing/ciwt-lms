#!/bin/sh
# Bring up X and Fluxbox on the Bochs framebuffer. Restarts if X exits.
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH HOME=/root DISPLAY=:0

# This X server does not open gzip-compressed PCF fonts. Expand them before X
# starts, or xterm and Fluxbox have nothing to draw with but the built-in font.
# A clean directory. X skips these bitmap fonts when they stay gzip-compressed
# in the packaged font path, and it does load them from a directory added with
# xset after the server is up.
font=/tmp/fonts
mkdir -p "$font"
if ls /usr/share/fonts/misc/*.pcf.gz >/dev/null 2>&1; then
  for f in /usr/share/fonts/misc/*.pcf.gz; do
    base=$(basename "$f" .gz)
    gzip -dc "$f" > "$font/$base"
  done
  cat > "$font/fonts.dir" << 'EOF'
6
6x13.pcf -misc-fixed-medium-r-semicondensed--13-120-75-75-c-60-iso10646-1
7x13.pcf -misc-fixed-medium-r-normal--13-120-75-75-c-70-iso10646-1
7x14.pcf -misc-fixed-medium-r-normal--14-130-75-75-c-70-iso10646-1
8x13.pcf -misc-fixed-medium-r-normal--13-120-75-75-c-80-iso10646-1
9x15.pcf -misc-fixed-medium-r-normal--15-140-75-75-c-90-iso10646-1
cursor.pcf cursor
EOF
  cat > "$font/fonts.alias" << 'EOF'
fixed -misc-fixed-medium-r-normal--13-120-75-75-c-70-iso10646-1
6x13 -misc-fixed-medium-r-semicondensed--13-120-75-75-c-60-iso10646-1
7x13 -misc-fixed-medium-r-normal--13-120-75-75-c-70-iso10646-1
7x14 -misc-fixed-medium-r-normal--14-130-75-75-c-70-iso10646-1
8x13 -misc-fixed-medium-r-normal--13-120-75-75-c-80-iso10646-1
9x15 -misc-fixed-medium-r-normal--15-140-75-75-c-90-iso10646-1
cursor cursor
EOF
fi

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
    rm -f /tmp/.X0-lock /tmp/.X11-unix/X0
  fi
  Xorg :0 -config /tmp/xorg.conf -nolisten tcp -noreset >/var/log/Xorg.log 2>&1 &
  i=0
  while ! DISPLAY=:0 xset q >/dev/null 2>&1 && [ "$i" -lt 50 ]; do
    usleep 100000 2>/dev/null || sleep 1
    i=$((i+1))
  done
  if DISPLAY=:0 xset q >/dev/null 2>&1; then
    DISPLAY=:0 xset +fp /tmp/fonts >/dev/null 2>&1 || true
    DISPLAY=:0 xset fp rehash >/dev/null 2>&1 || true
    echo NOVDESK_READY > /dev/ttyS0
    # Fluxbox's own root fill hits BadMatch on this 16-bit framebuffer.
    # Paint the root after Fluxbox is up; that fill is what the student sees.
    ( sleep 2; DISPLAY=:0 /usr/bin/nbg ) &
    fluxbox
  fi
  sleep 1
done
