#!/usr/bin/env python

import sys


def main(argv):
    item = ' '.join(argv[1:]) + '\n'
    lines = list(sys.stdin)
    if item in lines:
        sys.stdout.write(item)
    for line in lines:
        if line != item:
            sys.stdout.write(line)

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
