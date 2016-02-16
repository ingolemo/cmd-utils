#!/usr/bin/env python

import os
import sys


def parse_args(argv):
    if '--env' in argv:
        yield from dict(os.environ).items()
        return
    for var in argv[1:]:
        if '=' in var:
            key, __, value = (var.partition('='))
            yield key, value
        else:
            yield var, os.environ.get(var, '')


def variable_variants(var):
    yield '$' + var
    yield '${' + var + '}'


def main(argv):
    replacements = dict(parse_args(argv))

    for line in sys.stdin:
        for name, value in replacements.items():
            for variant in variable_variants(name):
                line = line.replace(variant, value)
        sys.stdout.write(line)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
