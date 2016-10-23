#!/usr/bin/env sh

# parses a file containing paths (one per line) and makes sure that
# those are in a path string that is printed to stdout
#
# intended use:
# PATH="$(parse-path pathfile)"

(
ORIGPATH="$PATH"

# if we can't find custom tools in path then we can do a little hack to
# see if they are in the path file's lines. This is a hack because it
# might do various forms of expansion that we don't want.
if ! (which varreplace && which rmdups && which decomment) >/dev/null 2>&1; then
	PATH="$(eval echo "$(cat "$1" | xargs echo | tr ' ' ':')"):$ORIGPATH"
fi

echo "$ORIGPATH" |
	tr ':' '\n' |
	cat "$1" - |
	varreplace --env |
	rmdups |
	decomment |
	xargs echo |
	tr ' ' ':'
)
