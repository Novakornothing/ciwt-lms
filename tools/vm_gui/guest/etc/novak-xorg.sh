#!/bin/sh
# Point X at the framebuffer and the PS/2 keyboard and mouse.
kb=""
ms=""
n=0
while [ "$n" -le 7 ]; do
  ev=/dev/input/event$n
  [ -e "$ev" ] || { n=$((n+1)); continue; }
  name=$(cat /sys/class/input/event$n/device/name 2>/dev/null)
  case "$name" in
    *[Mm]ouse*) ms=$ev ;;
    *[Kk]eyboard*) kb=$ev ;;
  esac
  n=$((n+1))
done
[ -n "$kb" ] || kb=/dev/input/event0
[ -n "$ms" ] || ms=/dev/input/event1
cat > /tmp/xorg.conf << EOF
Section "ServerFlags"
  Option "AutoAddDevices" "false"
  Option "DontVTSwitch" "true"
  Option "AllowMouseOpenFail" "true"
EndSection
Section "InputDevice"
  Identifier "Keyboard0"
  Driver "evdev"
  Option "Device" "$kb"
EndSection
Section "InputDevice"
  Identifier "Mouse0"
  Driver "evdev"
  Option "Device" "$ms"
EndSection
Section "Device"
  Identifier "Card0"
  Driver "fbdev"
  Option "fbdev" "/dev/fb0"
  Option "ShadowFB" "false"
EndSection
Section "Monitor"
  Identifier "Monitor0"
EndSection
Section "Screen"
  Identifier "Screen0"
  Device "Card0"
  Monitor "Monitor0"
  DefaultDepth 16
  SubSection "Display"
    Depth 16
    Modes "800x600"
  EndSubSection
EndSection
Section "ServerLayout"
  Identifier "Layout0"
  Screen "Screen0"
  InputDevice "Keyboard0" "CoreKeyboard"
  InputDevice "Mouse0" "CorePointer"
EndSection
EOF
