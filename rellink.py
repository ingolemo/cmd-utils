#!/usr/bin/env python
'''Create a relative symbolic link. Unlike `ln -s`, both the target and
the name should be specified relative to the current working directory.'''

import os
import sys
import argparse


def parse_name(name, target):
    name = os.path.abspath(name)
    if os.path.isdir(name):
        name = os.path.join(name, os.path.basename(target))
    return name


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target')
    parser.add_argument('name')
    parser.add_argument(
        '-a',
        '--absolute',
        action='store_true',
        help='Have the link be absolute instead'
    )
    opts = parser.parse_args(argv[1:])

    name = parse_name(opts.name, opts.target)
    target = os.path.abspath(opts.target)

    # target must exist
    if not os.path.exists(target):
        return 'can\'t find {}'.format(target)

    # name must not be linked to something else that exists
    if os.path.lexists(name):
        if not os.path.islink(name):
            return '{} exists and not a symlink'.format(name)
        elif not os.path.exists(name):
            # name is a broken link, just remove it and continue
            os.unlink(name)
        elif os.path.samefile(name, target):
            # everything is already correctly linked
            return
        else:
            return '{} exists and linked elsewhere'.format(name)

    if not opts.absolute:
        target = os.path.relpath(target, os.path.dirname(name))

    # print(target, name)
    os.symlink(target, name)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
