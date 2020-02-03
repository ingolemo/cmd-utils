#!/usr/bin/env python
'''Usage: datesort

Sorts lines of stdin based on the date embedded within. A date is any
substring matching the following regex:

    \d\d\d\d\.\d\d\.\d\d
'''

import re
import sys

regex = re.compile(r'\d\d\d\d\.\d\d\.\d\d')

def date_key(line):
    matches = regex.findall(line)
    date = matches[-1] if matches else '9999.99.99'
    return date, line


def main(argv):
    if '-h' in argv or '--help' in argv:
        return __doc__

    for line in sorted(sys.stdin, key=date_key):
        sys.stdout.write(line)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
