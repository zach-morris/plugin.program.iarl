#!/bin/bash
# App Launch Find Core script - Append -L <core> to the given command


# Check for agruments
if [ -z "$*" ]; then
	echo "No arguments provided."
	echo "Usage:"
	echo "$0 <core basename> [/path/to/]executable [arguments]"
	exit
fi

COREBASE=$1
shift

CORE=
for path in /usr/lib /usr/lib/x86_64-linux-gnu /usr/lib/i386-linux-gnu /usr/local/lib; do
    candidate="$path/libretro/$COREBASE"
    if [ -e "$candidate" ]; then
        CORE="$candidate"
        break
    fi
done

if [ -z "$CORE" ]; then
    echo "Core $COREBASE not found"
    exit 1
fi

exec "$@" -L "$CORE"
