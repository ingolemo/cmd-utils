#!/usr/bin/env python
"""
Usage: emptyfolder [folder]

Returns 0 if the folder is empty, 1 otherwise. If no folder is passed
on the command line then the current working directory is used.
"""

import os
import pathlib
import sys


def main(args):
    if "-h" in args or "--help" in args:
        return __doc__

    try:
        fname = args[1]
    except IndexError:
        fname = "."

    folder = pathlib.Path(fname).resolve()
    files = list(folder.iterdir())
    if files:
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
