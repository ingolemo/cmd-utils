#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: loop [-c] <subcommand>...

Run a command until it returns a non-zero status code. If the first
arg is -c then the second argument is the subcommand and it will
be run in a subshell. Otherwise, all the rest of the arguments are
the subcommand.

Examples:
	loop echo Hello
	loop -c 'echo Hello'
EOF
	exit 1
	;;
esac

if [ "$1" = '-c' ]; then
	while sh -c "$2"; do true; done
else
	while "$@"; do true; done
fi
