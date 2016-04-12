BASE_DIR=~/retroarch/default
CORE_DIR=$BASE_DIR/libretro/cores
LD_LIBRARY_PATH=$BASE_DIR/lib

PROG=xbmc.bin
pgrep kodi.bin >> /dev/null && PROG=kodi.bin

help() {
  echo "Usage: $0 core_name rom_path"
  echo "Example: $0 snes9x_next $BASE_DIR/share/rom/snes/classickong.smc"
  exit 1
}

[ "$1" == "" ] && help
[ "$2" == "" ] && help
[ ! -f "$CORE_DIR/$1_libretro.so" ] && echo "Core '$CORE_DIR/$1_libretro.so' not found!"
[ ! -f "$2" ] && echo "ROM file '$2' not found!"

pgrep $PROG | xargs kill -SIGSTOP
$BASE_DIR/bin/retroarch -c $BASE_DIR/config/retroarch.cfg -L $CORE_DIR/$1_libretro.so "$2"
pgrep $PROG | xargs kill -SIGCONT

