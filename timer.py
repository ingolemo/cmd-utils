#!/usr/bin/env python

import sys
import time
import datetime


def main(argv):
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
