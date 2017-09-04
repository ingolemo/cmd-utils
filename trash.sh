#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: trash <file>

Moves the file to your trash, as specified by XDG specs. This is usually
the ~/.local/Trash folder.
EOF
	exit 1
	;;
esac

mv "$@" "${XDG_DATA_HOME:-$HOME/.local}/Trash/files"
