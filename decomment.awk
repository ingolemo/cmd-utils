#!/usr/bin/awk -f
# a filter that deletes lines from stdin that start with the hash
# character and blank lines
$0 !~ /^(\w*#.*)?$/
