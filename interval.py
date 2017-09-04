#!/usr/bin/env python

'''Usage: interval

Takes a stream of numbers on stdin and prints the intervals between
adjacent numbers. Example:

    $ printf '1\\n2\\n4\\n1' | interval
    1.0
    2.0
    -3.0
'''

import sys


def pairs(iterable):
    iterator = iter(iterable)
    old = next(iterator)
    for new in iterator:
        yield old, new
        old = new


def main(argv):
    if '-h' in argv or '--help' in argv:
        return __doc__

    for pre, post in pairs(sys.stdin):
        print(float(post.strip()) - float(pre.strip()))


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
