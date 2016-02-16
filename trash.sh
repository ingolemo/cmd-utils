#!/usr/bin/env sh

mv "$@" "${XDG_DATA_HOME:-$HOME/.local}/Trash/files"
