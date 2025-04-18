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

import argparse
import difflib
import os
import pathlib
import random
import subprocess
import sys
from typing import Iterable, Optional

REMOVE_CMDS = {"delete", "remove", "rm", "del", "unlink"}


def walk(file: pathlib.Path, max_depth: None | int = None) -> Iterable[pathlib.Path]:
    file = file.resolve()
    if file.is_dir():
        if max_depth is not None and max_depth <= 0:
            yield file
            return

        new_depth = None if max_depth is None else max_depth - 1
        for subfile in file.iterdir():
            yield from walk(subfile, max_depth=new_depth)
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
FG_BLACK = "\033[30m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"


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
                result.append(BOLD)
                result.append(FG_BLACK)
                result.append(BG_RED)
                result.append(left_fragment)
                result.append(BG_GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif op == "insert":
                result.append(BOLD)
                result.append(FG_BLACK)
                result.append(BG_GREEN)
                result.append(right_fragment)
                result.append(RESET)
            elif op == "delete":
                result.append(BOLD)
                result.append(FG_BLACK)
                result.append(BG_RED)
                result.append(left_fragment)
                result.append(RESET)
            else:
                raise Exception(f"Unknown opcode: {op}")
    return "".join(result)


def sort_files(
    files: dict[pathlib.Path, Optional[pathlib.Path]],
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


def parse_args(argv):
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("-d", "--max-depth", type=int, default=None)
    parser.add_argument("files", nargs="*", default=["."])
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int | str:
    args = parse_args(argv)

    all_files: list[pathlib.Path] = []
    for arg_file in args.files:
        all_files.extend(walk(pathlib.Path(arg_file), max_depth=args.max_depth))
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
