#!/usr/bin/awk -f
# a filter that removes all lines from stdin that aren't comments
# (lines starting with the hash character)
/^\w*#.*$/
