#!/usr/bin/env python
"""Usage: mvi [file]...

Takes a list of files or directories and presents their paths in an
editor window (using $EDITOR, falling back to `vi`). The user
can edit the paths to rename files and directories en mass.

This utility never deletes files, but it will delete directories that
were made empty because all of the files were moved out of them. Lines
deleted from the editor will be ignored.

The name is a pun on `mv` and `vi`.

The code is somewhat careful not to lose any data, but it's hard to know
all the edge cases in situations like this. USE AT YOUR OWN RISK!"""

import pathlib
import os
import subprocess
import sys
import tempfile


def walk(file):
    file = pathlib.Path(file).resolve()
    if file.is_dir():
        for subfile in file.iterdir():
            yield from walk(subfile)
    elif file.is_file():
        yield file


def move(source, dest):
    print(f"Moving file\n\tFrom: {source}\n\tTo:   {dest}")
    if dest.exists():
        print("But destination already exists.")
        answer = input("Overwrite? ")
        if not answer.lower().startswith("y"):

            raise Exception(
                f"Cannot move {source} to {dest}, destination already exists"
            )

    dest.parent.mkdir(parents=True, exist_ok=True)

    source.rename(dest)
    for parent in source.parents:
        contents = list(parent.iterdir())
        if contents:
            break
        parent.rmdir()


def main(args):
    if len(args) > 1 and args[1] in {"-h", "--help"}:
        print(__doc__)
        return

    arg_files = args[1:]
    if not arg_files:
        arg_files = ["."]

    all_files = []
    for arg_file in arg_files:
        all_files.extend(walk(arg_file))
    all_files.sort()

    max_n = len(str(len(all_files)))

    pid = os.getpid()
    fname = pathlib.Path(f"/tmp/mvi_{pid}.txt")
    with fname.open("w") as handle:
        for n, line in enumerate(all_files):
            print(f"{n:0{max_n}} {line}", file=handle)

    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(fname)])

    with fname.open("r") as handle:
        for line in handle:
            n, line = line.strip().split(" ", 1)
            source = all_files[int(n)]
            dest = pathlib.Path(line)
            if source != dest:
                move(source, dest)

    fname.unlink()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
