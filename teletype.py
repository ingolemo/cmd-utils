#!/usr/bin/env python

import sys
import time

default = 0.1
timings = {
    ' ': 0.2,
    '\n': 0.9,

    # punctuation
    '.': 0.4, ',': 0.4, ';': 0.4, '?': 0.4, '!': 0.4,
}


def main(argv):
    for line in sys.stdin:
        for char in line:
            sys.stdout.write(char)
            sys.stdout.flush()

            time.sleep(timings.get(char, default))

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
