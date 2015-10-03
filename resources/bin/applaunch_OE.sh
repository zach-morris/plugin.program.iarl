#!/bin/bash
# App Launch script - Quit Kodi to launch RetroArch
# Taken from the OpenElec Forums for use with IARL

BASE_DIR=/storage/retroarch/default
RETROARCH=$BASE_DIR/bin/retroarch
CONFIG=$BASE_DIR/config/retroarch.cfg
CORES=$BASE_DIR/libretro/cores
CORE=$CORES/$1_libretro.so

if [ ! -f "$2" ]
then
  pgrep kodi.bin | xargs kill -SIGSTOP
  sleep 1
  LD_LIBRARY_PATH=$BASE_DIR/lib
  $RETROARCH --menu -c $CONFIG
  while [ $(pidof retroarch) ];do
  usleep 200000
  done;
  rm /var/lock/kodi.disabled
  pgrep kodi.bin | xargs kill -SIGCONT
#  echo "Test"
  exit 1
fi

if [ -f "$2.cfg" ]; then
  echo "Config file for `basename "$2"` found, using."
  EXTRAFLAG="--appendconfig "$2.cfg""
fi

###If you wish to kill Kodi on each game launch, uncomment these lines and comment out the next set of code.
#systemctl stop xbmc.service
#systemctl stop kodi.service
#LD_LIBRARY_PATH=$BASE_DIR/lib $RETROARCH -c $CONFIG $EXTRAFLAG -L $CORE "$2"
#systemctl start xbmc.service
#systemctl start kodi.service

pgrep kodi.bin | xargs kill -SIGSTOP
sleep 1
echo LD_LIBRARY_PATH=$BASE_DIR/lib $RETROARCH -c $CONFIG $EXTRAFLAG -L $CORE "$2"
LD_LIBRARY_PATH=$BASE_DIR/lib $RETROARCH -c $CONFIG $EXTRAFLAG -L $CORE "$2" &
while [ $(pidof retroarch) ];do
usleep 200000
done;

rm /var/lock/kodi.disabled
pgrep kodi.bin | xargs kill -SIGCONT 