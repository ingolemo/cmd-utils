#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: lnbin <target>

Creates a symlink to a file in the user's bin directory
(~/.local/bin). The symlink will not have a file extension if
it matches a common executable extension.
EOF
	exit 0
	;;
esac

bindir="$HOME/.local/bin"
target="$1"
name="$(basename $target | tr '_' '-')"

for suff in .sh .py .bash .fish .pl .rb .awk; do
    name="${name/$suff/}"
done

exec rellink "$target" "$bindir/$name"
