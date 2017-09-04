#!/usr/bin/env python
'''Usage: hashsort

Sorts lines in stdin according to the hash of those lines. Outputs
the lines in a deterministic order that is hard to predict; a sort of
non-random shuffle.
'''

import sys
import hashlib


def myhash(string):
    bytelist = string.strip('\n').encode()
    return hashlib.sha256(bytelist).hexdigest()


def main(argv):
    if '--help' in argv or '-h' in argv:
        return __doc__

    for line in sorted(sys.stdin, key=myhash):
        sys.stdout.write(line)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
