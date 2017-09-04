#!/usr/bin/env sh
# a filter that adds a new blank line between each line of stdin

sed 's/$/\n/g'
