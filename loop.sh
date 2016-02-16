#!/usr/bin/env sh

if [ "$1" = '-c' ]; then
	while sh -c "$2"; do true; done
else
	while "$@"; do true; done
fi
