#!/usr/bin/env sh

dir="${1:-"$(pwd)"}"
ls --sort=time --time=access --reverse "$dir" | head -n1
