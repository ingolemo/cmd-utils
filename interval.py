#!/usr/bin/env python

import sys


def pairs(iterable):
    iterator = iter(iterable)
    old = next(iterator)
    for new in iterator:
        yield old, new
        old = new


def main(argv):
    for pre, post in pairs(sys.stdin):
        print(float(post.strip()) - float(pre.strip()))


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
