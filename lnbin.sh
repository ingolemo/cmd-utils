#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: lnbin <target>

Creates a symlink to a file in the user's bin directory
(~/.local/bin). `lnbin` will strip the file extension if
it matches a common executable extension.
EOF
	exit 0
	;;
esac

bindir="$HOME/.local/bin"
target="$1"
name="$(basename $target | tr '_' '-')"
extensions=".sh .py .bash .fish .pl .rb .awk"

for suff in $extensions; do
    name="${name%$suff}"
done

exec rellink "$target" "$bindir/$name"
