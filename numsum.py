#!/usr/bin/env python

# from num-utils
# http://suso.suso.org/programs/num-utils

import sys


def main(argv):
    print(sum(float(n) for n in sys.stdin))


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
