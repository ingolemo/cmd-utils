#!/usr/bin/env python
"""Usage: teletype

A filter that outputs stdin one charactor at a time to simulate someone
typing at an old teletype machine.
"""

import sys
import time

default = 0.1
timings = {
    " ": 0.2,
    "\n": 0.9,
    # punctuation
    ".": 0.4,
    ",": 0.4,
    ";": 0.4,
    "?": 0.4,
    "!": 0.4,
}


def main(argv):
    for line in sys.stdin:
        for char in line:
            sys.stdout.write(char)
            sys.stdout.flush()

            time.sleep(timings.get(char, default) * 0.5)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
