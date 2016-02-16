#!/usr/bin/env python

import sys
import subprocess
import functools


def pipe(cmd, input):
    p = subprocess.PIPE
    proc = subprocess.Popen(cmd, stdin=p, stdout=p)
    stdout, _ = proc.communicate(input.encode())
    return stdout.decode()


def main(argv):
    my_key = functools.partial(pipe, argv[1:])
    for line in sorted(sys.stdin, key=my_key):
        sys.stdout.write(line)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
