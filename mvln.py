#!/usr/bin/env python
"""Moves a file from source to destination while leaving a symlink at the
source that points to the destination. Follows symlinks in both source
and destination because it doesn't make much sense to move a symlink
just to put on in it's place.

The name is a combination of `mv` and `ln`."""

import argparse
import os
import pathlib
import sys


def main(args: list[str]) -> int | str:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("destination", type=pathlib.Path)
    parser.add_argument("-f", "--force", action="store_true")
    arguments = parser.parse_args(args[1:])
    source = arguments.source
    dest = arguments.destination

    if not source.exists():
        return f"{source}: does not exist"
    if dest.is_dir():
        dest = dest / source.name
    if dest.exists():
        if not force:
            return "Destination already exists"
        if source.samefile(dest):
            return "Cannot move a file onto itself"
    if not dest.parent.exists():
        return f"No such folder {dest.parent}"

    source.rename(dest)
    if dest.is_absolute():
        source.symlink_to(dest.resolve())
    else:
        relative_dest = os.path.relpath(dest, source.parent)
        source.symlink_to(relative_dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
