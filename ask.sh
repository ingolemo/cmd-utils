#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: ask <question>...

Asks the user a question and returns 1 if the user answered no,
returns 0 otherwise
EOF
	exit 1
	;;
esac

echo -n "$@"' '
read answer
new_ans="$(echo "$answer" | cut -c1 | tr N n)"
if [ "$new_ans" = 'n' ]; then
	exit 1
else
	exit 0
fi
