#!/usr/bin/env python
'''Usage: varreplace (--env|[VARIABLE=VALUE]...)

Replaces variables in stdin with their values. Many variables can be given
on the command line in the same format as expected by `export`, or you
can use the --env flag to use variables from the environment. Variables
in stdin are strings like $var or ${var}.

Example:
    $ echo 'Praise be to ${DIETY}.' | varreplace DIETY=Iluvatar
    Praise be to Iluvatar.
    $ echo 'Display number: "$DISPLAY"' | varreplace --env
    Display number: ":0" '''

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
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    replacements = dict(parse_args(argv))

    for line in sys.stdin:
        for name, value in replacements.items():
            for variant in variable_variants(name):
                line = line.replace(variant, value)
        sys.stdout.write(line)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
