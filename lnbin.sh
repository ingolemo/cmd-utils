#!/usr/bin/env sh

bindir="$HOME/.local/bin"
target="$1"
name="$(basename $target | tr '_' '-')"

for suff in .sh .py .bash .pl .rb; do
    name="${name/$suff/}"
done

exec rellink "$target" "$bindir/$name"
