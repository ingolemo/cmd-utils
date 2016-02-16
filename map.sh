#!/usr/bin/env sh

exec xargs -d '\n' -I {} "$@"
