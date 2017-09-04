#!/usr/bin/env sh

# noop is a "no operation" pipe command completely and utterly useless
# does nothing itself, but is handy if a command alters its behaviour when
# attached to a tty (harmless example: `ls --color=auto` vs `ls --color=auto
# | noop`)

# may have other uses
exec cat -
