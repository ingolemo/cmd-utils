#!/usr/bin/env sh

case "$1" in
'-h'|'--help')
	cat <<EOF
Usage: oldestfile [directory]

Prints the basename of the oldest file or folder in the given
directory. If no directory is given then the cwd is assumed.
EOF
	exit 1
	;;
esac

dir="${1:-"$(pwd)"}"
ls --sort=time --time=access --reverse "$dir" | head -n1
