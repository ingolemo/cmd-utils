#!/usr/bin/env python
'''Usage: timepick [second|minute|hour|day|week]

A filter that picks a single line from stdin based on the current time.

This has an advantage over random selection in that it's cyclical and
thus no clustering or repetition of the selections; seems 'more random'
to people.
'''

import os
import sys
import datetime

pdict = {
    'second': lambda a: (a.days * 24 * 60 * 60) + a.seconds,
    'minute': lambda a: (a.days * 24 * 60) + (a.seconds / 60),
    'hour': lambda a: (a.days * 24) + (a.seconds / 3600),
    'day': lambda a: a.days,
    'week': lambda a: a.days / 7,
}


def numSinceEpoch(period):
    td = datetime.datetime.now() - datetime.datetime.fromtimestamp(0)
    return abs(int(pdict[period](td)))


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    try:
        div = argv[1]
        if div.endswith('s'):
            div = div[:-1]
    except IndexError:
        div = object()

    if div not in pdict:
        return 'usage: {0} [{1}]'.format(
            os.path.basename(argv[0]), '|'.join(sorted(pdict.keys()))
        )

    choices = sys.stdin.readlines()
    try:
        lineno = numSinceEpoch(div) % len(choices)
    except ZeroDivisionError:
        pass
    else:
        choice = choices[lineno].strip()
        print(choice)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
