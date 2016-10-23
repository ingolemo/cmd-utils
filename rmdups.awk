#!/usr/bin/awk -f

# this filter reads a list of newline seperated items from stdin
# and removes any lines that are duplicates of an already output line

!($0 in array) {
	array[$0]
	print
}

