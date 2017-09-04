#!/usr/bin/env python
'''Usage: slower [wait]

A filter that outputs one line every \`wait\` seconds. Default wait is
1 second.
'''

import sys
import time


def slower(wait):
    for line in sys.stdin:
        sys.stdout.write(line)
        time.sleep(wait)


def main(argv):
    if '-h' in argv or '--help' in argv:
        return __doc__

    try:
        wait = float(argv[1])
    except (IndexError, ValueError):
        wait = 1.0

    return slower(wait)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
