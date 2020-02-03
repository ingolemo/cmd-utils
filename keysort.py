#!/usr/bin/env python
"""Usage: keysort <subcommand>...

Sorts lines of stdin based on the output of feeding that line into the
stdin of the subcommand. Allows you to sort a stream based on things
other than the contents of the stream itself.

In this example we sort files in the current working directory by their last modified time:

    ls | keysort xargs stat --format %Y
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

    my_key = functools.partial(pipe, argv[1:])
    for line in sorted(sys.stdin, key=my_key):
        sys.stdout.write(line)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
