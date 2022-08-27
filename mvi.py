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

import difflib
import os
import pathlib
import random
import subprocess
import sys


def walk(file):
    file = pathlib.Path(file).resolve()
    if file.is_dir():
        for subfile in file.iterdir():
            yield from walk(subfile)
    elif file.is_file():
        yield file


def maybe_remove_parents(source: pathlib.Path):
    for parent in source.parents:
        contents = list(parent.iterdir())
        if contents:
            break
        parent.rmdir()


def delete(source):
    answer = input("Are you sure you want to delete it? ")
    if not answer.lower().startswith("y"):
        raise Exception()

    source.unlink()
    maybe_remove_parents(source)


def move(source, dest):
    if dest.exists():
        print("But destination already exists.")
        if source.samefile(dest):
            print("They are hardlinks for one another.")
        answer = input("Overwrite? ")
        if not answer.lower().startswith("y"):

            raise Exception(
                f"Cannot move {source} to {dest}, destination already exists"
            )

    dest.parent.mkdir(parents=True, exist_ok=True)
    source.rename(dest)
    maybe_remove_parents(source)


def edit(string: str) -> str:
    pid = os.getpid()
    rand = random.randrange(0, 10000)
    fname = pathlib.Path(f"/tmp/mvi_pid{pid}_rand{rand:04}.txt")
    fname.write_text(string)

    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(fname)])

    result = fname.read_text()
    fname.unlink()
    return result


RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"


def diff(left: str, right: str) -> str:
    matcher = difflib.SequenceMatcher(None, left, right)
    result = []
    opcodes = list(matcher.get_grouped_opcodes(n=1000000))
    for opcode in opcodes:
        for opcode_data in opcode:
            opcode, left_start, left_end, right_start, right_end = opcode_data
            left_fragment = left[left_start:left_end]
            right_fragment = right[right_start:right_end]
            if opcode == "equal":
                assert left_fragment == right_fragment
                result.append(left_fragment)
            elif opcode == "replace":
                result.append(RED)
                result.append(left_fragment)
                result.append(GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif opcode == "insert":
                result.append(GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif opcode == "delete":
                result.append(RED)
                result.append(left_fragment)
                result.append(RESET)
            else:
                raise Exception(opcode)
    return "".join(result)


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
    if not all_files:
        return "No files selected"

    max_n = len(str(len(all_files)))
    string = "\n".join(f"{n:0{max_n}} {file}" for n, file in enumerate(all_files))

    result = edit(string)

    for line in result.splitlines():
        n, line = line.strip().split(" ", 1)
        source = all_files[int(n)]

        if line in {"delete", "remove", "rm"}:
            print("rm", source)
            delete(source)
            continue

        dest = pathlib.Path(line)
        if source != dest:
            print("mv", diff(str(source), str(dest)))
            move(source, dest)
            continue


if __name__ == "__main__":
    sys.exit(main(sys.argv))
