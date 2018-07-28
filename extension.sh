#!/usr/bin/env sh

usage=<<EOF
Usage: extension <file>

Prints the extension of the file to stdout, without the dot. Just a
fancy wrapper that allows the following code to be used in pipelines
and shell-outs:

	echo "${1##*.}"
EOF

case "$1" in
''|'-h'|'--help')
	echo $usage
	exit 1
	;;
esac

if [ "$#" -ne 1 ]; then
	echo $usage
	exit 1
fi

echo "${1##*.}"
