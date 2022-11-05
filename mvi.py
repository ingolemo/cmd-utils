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
from typing import Iterable, Optional

REMOVE_CMDS = {"delete", "remove", "rm", "del", "unlink"}


def walk(file: pathlib.Path) -> Iterable[pathlib.Path]:
    file = file.resolve()
    if file.is_dir():
        for subfile in file.iterdir():
            yield from walk(subfile)
    elif file.is_file():
        yield file


def maybe_remove_parents(source: pathlib.Path) -> None:
    for parent in source.parents:
        contents = list(parent.iterdir())
        if contents:
            break
        parent.rmdir()


def move(source: pathlib.Path, dest: pathlib.Path) -> None:
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
            op, left_start, left_end, right_start, right_end = opcode_data
            left_fragment = left[left_start:left_end]
            right_fragment = right[right_start:right_end]
            if op == "equal":
                assert left_fragment == right_fragment
                result.append(left_fragment)
            elif op == "replace":
                result.append(RED)
                result.append(left_fragment)
                result.append(GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif op == "insert":
                result.append(GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif op == "delete":
                result.append(RED)
                result.append(left_fragment)
                result.append(RESET)
            else:
                raise Exception(f"Unknown opcode: {op}")
    return "".join(result)


def sort_files(
    files: dict[pathlib.Path, Optional[pathlib.Path]]
) -> Iterable[tuple[pathlib.Path, Optional[pathlib.Path]]]:
    files = files.copy()
    while files:
        candidates = [
            (source, dest)
            for source, dest in files.items()
            if dest is None or dest not in files
        ]
        if not candidates:
            raise Exception("filename cycle detected")
        for source, dest in candidates:
            yield source, dest
            del files[source]


def try_commit_file_changes(files: dict[pathlib.Path, Optional[pathlib.Path]]) -> None:
    deletions = [source for source, dest in files.items() if dest is None]

    if deletions:
        print("The following files will be deleted:")
        for deletion in deletions:
            print(f"\t{deletion}")
        answer = input("Confirm? ")
        if not answer.lower().startswith("y"):
            raise Exception()

    for source, dest in sort_files(files):
        if dest is None:
            print("rm", source)
            source.unlink()
            maybe_remove_parents(source)
        else:
            print("mv", diff(str(source), str(dest)))
            move(source, dest)


def main(args: list[str]) -> int | str:
    if len(args) > 1 and args[1] in {"-h", "--help"}:
        print(__doc__)
        return 0

    arg_files = args[1:]
    if not arg_files:
        arg_files = ["."]

    all_files: list[pathlib.Path] = []
    for arg_file in arg_files:
        all_files.extend(walk(pathlib.Path(arg_file)))
    all_files.sort()
    if not all_files:
        return "No files selected"

    max_n = len(str(len(all_files)))
    string = "\n".join(f"{n:0{max_n}} {file}" for n, file in enumerate(all_files))

    result = edit(string)

    file_changes: dict[pathlib.Path, Optional[pathlib.Path]] = dict()

    for line in result.splitlines():
        n, line = line.strip().split(" ", 1)
        source = all_files[int(n)]

        if line.lower() in REMOVE_CMDS:
            file_changes[source] = None
            continue

        dest = pathlib.Path(line)
        if source != dest:
            file_changes[source] = dest
            continue

    try_commit_file_changes(file_changes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
