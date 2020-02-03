#!/usr/bin/env python
"""Usage: linewise <subcommand>...

Runs a sub-command for each line in stdin, writing that line into the
stdin of the sub-command and concatenating the outputs. Similar to xargs
except that it uses stdin instead of command-line arguments.
"""

import sys
import subprocess
import functools


def pipe(cmd, input):
    p = subprocess.PIPE
    proc = subprocess.Popen(cmd, stdin=p, stdout=p)
    stdout, _ = proc.communicate(input.encode())
    return stdout.decode()


def main(argv):
    if not argv[1:] or "-h" in argv or "--help" in argv:
        return __doc__

    for line in sys.stdin:
        sys.stdout.write(pipe(argv[1:], line))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
