#!/usr/bin/env python

import sys
import subprocess


def main(argv):
    with open('/dev/null', 'w') as fd:
        retcode = subprocess.call(argv[1:], stdout=fd, stderr=fd)
    print(retcode)
    return retcode

if __name__ == '__main__':
    sys.exit(main(sys.argv))
