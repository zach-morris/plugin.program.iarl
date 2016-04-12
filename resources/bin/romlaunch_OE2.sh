#ROM Launch Script for use with IARL
#By Zach Morris
#This is about as simple as it gets

pgrep "kodi.bin" | xargs kill -SIGSTOP
"$@"
pgrep "kodi.bin" | xargs kill -SIGCONT