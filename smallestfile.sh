#!/usr/bin/env sh

dir="${1:-"$(pwd)"}"
ls --sort=size --reverse "$dir" | head -n1
