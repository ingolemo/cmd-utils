#!/usr/bin/env python

import sys


def main(argv):
    output = [line for line in sys.stdin.buffer]
    with open(argv[1], 'wb') as file:
        for bytes in output:
            file.write(bytes)

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
