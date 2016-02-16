#!/usr/bin/env sh

# this filter reads a list of newline seperated items from stdin
# and removes any lines that are duplicates of an already output line

awk '!($0 in array) { array[$0]; print }'

