#!/usr/bin/env sh

# Just a fancier diff with color pager support
# A middle ground between diff and vimdiff

diff --unified --color=always "$@" | less -R
