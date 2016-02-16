#!/usr/bin/env sh

string="$1"
substring="$2"
if [ "${string#*$substring}" != "$string" ]; then
	exit 0
else
	exit 1
fi
