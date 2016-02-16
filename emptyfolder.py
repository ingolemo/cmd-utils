#!/usr/bin/env python

import os
import pathlib
import sys

def main(args):
    try:
        fname = args[1]
    except IndexError:
        fname = '.'

    folder = pathlib.Path(fname).resolve()
    files = list(folder.iterdir())
    if files:
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
