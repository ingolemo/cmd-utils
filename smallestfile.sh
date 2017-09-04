#!/usr/bin/env sh

case "$1" in
'-h'|'--help')
	cat <<EOF
Usage: smallestfile [directory]

Prints the smallest file in the specified directory. If a directory is
not given thenthe current working directory is used.
EOF
	exit 1
	;;
esac

dir="${1:-"$(pwd)"}"
ls --sort=size --reverse "$dir" | head -n1
