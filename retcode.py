#!/usr/bin/env python
'''Usage: retcode <subcommand>...

Runs the subcommand and prints its return code. Discards the subcommand's
stdout and stderr.'''

import sys
import subprocess


def main(argv):
    if not argv[1:] or argv[1] == '-h' or argv[1] == '--help':
        return __doc__

    with open('/dev/null', 'w') as fd:
        retcode = subprocess.call(argv[1:], stdout=fd, stderr=fd)
    print(retcode)
    return retcode

if __name__ == '__main__':
    sys.exit(main(sys.argv))
