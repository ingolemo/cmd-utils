#!/usr/bin/env python

import sys
import time


def slower(wait):
    for line in sys.stdin:
        sys.stdout.write(line)
        time.sleep(wait)


def main(argv):
    try:
        wait = float(argv[1])
    except (IndexError, ValueError):
        wait = 1.0

    return slower(wait)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
