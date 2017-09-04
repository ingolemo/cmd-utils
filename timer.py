#!/usr/bin/env python
'''Usage: timer

Counts the time since this program was started, printing it to stdout
every second.'''

import sys
import time
import datetime


def main(argv):
    if '-h' in argv or '--help' in argv:
        return __doc__

    start = datetime.datetime.now()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print(datetime.datetime.now() - start)
            return
        else:
            print(datetime.datetime.now() - start, end='\r')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
