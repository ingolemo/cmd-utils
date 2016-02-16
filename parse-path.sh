#!/usr/bin/env sh

# parses a file containing paths (one per line) and makes sure that
# those are in a path string that is printed to stdout
#
# intended use:
# PATH="$(parse-path pathfile)"

/usr/bin/echo $PATH |
	/usr/bin/tr ':' '\n' |
	/usr/bin/cat "$1" - |
	$HOME/.local/bin/varreplace --env |
	$HOME/.local/bin/rmdups |
	$HOME/.local/bin/decomment |
	/usr/bin/xargs echo |
	/usr/bin/tr ' ' ':'
