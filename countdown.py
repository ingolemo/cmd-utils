#!/usr/bin/env python

import datetime
import re
import sys
import time

def parse(args):
    arg = args[1]
    regex = r'((?P<h>[0-9]+)h)?((?P<m>[0-9]+)m?)??((?P<s>[0-9]+)s)?'
    match = re.fullmatch(regex, arg)
    if not match:
        raise ValueError('cannot parse string')
    d = match.groupdict()

    times = [d.get(a, 0) or 0 for a in 'hms']
    h, m, s = [int(a) for a in times]
    return datetime.timedelta(seconds=(h * 60 + m) * 60 + s)

def main(argv):
    try:
        length = parse(argv)
    except (IndexError, ValueError):
        return 'usage: countdown [hours]h[minutes]m[seconds]s'
    start = datetime.datetime.now()

    while True:
        now = datetime.datetime.now()
        passed = now - start
        left = length - passed
        print(left, end='\r')
        if passed > length:
            break
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
