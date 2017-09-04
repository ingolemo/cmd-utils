#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: runlines <subcommand>

A more usable front-end to xargs that passes the following flags:

    -d '\\n' -I {} -L 1

These mean that it will use the newline as an item separator, replace {}
in the subcommand with the item, and run a new instance of the subcommand
for each line.
EOF
	exit 1
	;;
esac

exec xargs -d '\n' -I {} -L 1 "$@"
