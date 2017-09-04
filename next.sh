#!/usr/bin/env sh

case "$1" in
''|'-h'|'--help')
	cat <<EOF
Usage: next <target> <args>...

Executes the next instance of a command with a certain name found in
the path. This is useful when you want to have a script shadow a system
utility, but also be able to call that system utility. For example, if
an ls command exists in both /usr/bin and /usr/local/bin then \`next
/usr/bin/ls args\` will execute \`/usr/local/bin/ls args\`. Put \`exec next
"\$0" --color=auto "\$@"\` in a file called \`ls\` somewhere high on your
path and all invocations of \`ls\` will have color.
EOF
	exit 1
	;;
esac

dir=${1%/*}
bin=${1##*/}
shift

unset flag
set -f
IFS=:

for d in $PATH; do
if [ "$d" = "$dir" ]; then
	flag=1
elif [ -n "$flag" ] && [ -x "$d/$bin" ]; then
	exec "$d/$bin" "$@"
fi
done

printf "%s: no '%s' found beyond '%s' in \$PATH\n" "${0##*/}" "$bin" "$dir" >&2
exit 127 
