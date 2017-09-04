#!/usr/bin/env python

'''Usage: filter <subcommand>...

This script can filter the contents of stdin by reading it line by
line and passing that line to a sub-command specified on the command line.
If the subcommand returns 0 then the line is allowed through otherwise
it is filtered.

Intended to be used with "test", but works with any subcommand. This
example finds all the files that are directories (It's a worse version of
`find -type d`):

    find | filter test -d

Take care to properly escape the sub-command.
'''

import sys
import shlex
import subprocess


def test(command, line):
    cmdline = shlex.split(command)
    cmdline = (cmdline.replace('{}', line) if '{}' in cmdline else
               cmdline + [line])

    return subprocess.call(cmdline) == 0


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    cmd = ' '.join(argv[1:])
    for line in sys.stdin:
        if test(cmd, line.strip()):
            sys.stdout.write(line)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
