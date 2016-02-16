#!/usr/bin/env python

import sys
import hashlib


def myhash(string):
    bytelist = string.strip('\n').encode()
    return hashlib.sha256(bytelist).hexdigest()


def main(argv):
    for line in sorted(sys.stdin, key=myhash):
        sys.stdout.write(line)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
