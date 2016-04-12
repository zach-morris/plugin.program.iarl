#!/bin/bash
# App Launch script - Quit Kodi to launch another program
# Edited for android by Zach Morris for use with IARL


# Check for agruments
if [ -z "$*" ]; then
	echo "No arguments provided."
	echo "Usage:"
	echo "applaunch.sh [/path/to/]executable [arguments]"
	exit
fi


Kodi_PID=$(ps | grep org.xbmc | awk '{print $2}')
Kodi_BIN=$'am start --user 0 -a android.intent.action.MAIN -n org.xbmc.xbmc/android.app.NativeActivity'

# Is Kodi running?
if [ -n $Kodi_PID ]
then
	kill -1 $Kodi_PID # Shutdown nice
	echo "Shutdown nice"
else
	echo "This script should only be run from within Kodi."
	exit
fi

# Wait for the kill
# sleep 

# Is Kodi still running?
if [ -n $Kodi_PID ]
then
    kill -9 $Kodi_PID # Force immediate kill
	echo "Shutdown hard"	
fi

echo "$@"

# Launch app - escaped!
"$@"

# Done? Restart Kodi
$Kodi_BIN &