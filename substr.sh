#!/usr/bin/env sh

# Tests if a string contains a substring.

# Usage: substr substring string

substring="$1"
string="$2"
if [ "${string#*$substring}" != "$string" ]; then
	exit 0
else
	exit 1
fi
