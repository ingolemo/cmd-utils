#!/usr/bin/env python

import argparse
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("blacklist", nargs="*")
    parser.add_argument("--min", type=int)
    parser.add_argument("--max", type=int)
    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    stdin = sys.stdin.read().strip()
    if stdin in args.blacklist:
        return
    if args.min is not None and int(stdin) < args.min:
        return
    if args.max is not None and int(stdin) > args.max:
        return
    print(stdin)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
