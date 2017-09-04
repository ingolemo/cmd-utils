#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: substr <substring> <string>

Returns 0 if the string contains the substring. Otherwise returns 1.
EOF
	exit 1
	;;
esac

# Tests if a string contains a substring.

# Usage: substr substring string

substring="$1"
string="$2"
if [ "${string#*$substring}" != "$string" ]; then
	exit 0
else
	exit 1
fi
