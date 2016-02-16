#!/usr/bin/env python

# This script can filter the content of a pipe by reading it
# line by line and passing it to a subcommand specified on the commandline
# if the subcommand returns 0 then the line is allowed through otherwise
# it is filtered
#
# Intended to be used with "test", but works with any subcommand.
#     find | filter test -d
#
# Take care to properly escape the command

import sys
import shlex
import subprocess


def test(command, line):
    cmdline = shlex.split(command)
    cmdline = (cmdline.replace('{}', line) if '{}' in cmdline else
               cmdline + [line])

    return subprocess.call(cmdline) == 0


def main(argv):
    cmd = ' '.join(argv[1:])
    for line in sys.stdin:
        if test(cmd, line.strip()):
            sys.stdout.write(line)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
