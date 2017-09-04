#!/usr/bin/env python
'''Usage: promote <data>...

A filter that promotes a certain line to the top of its output, leaving
all the other lines in their original order. If the line does not appear
in the input then it will not be added and this filter is a no-op.

Example:
    $ printf '1\\n2\\n3' | promote 2
    2
    1
    3'''

import sys


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

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
