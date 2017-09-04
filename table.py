#!/usr/bin/env python
'''A filter that aligns the columns in stdin.'''

import argparse
import itertools
import os
import sys


def make_padding(pad, sep):
    if sep is None or sep.isspace():
        return pad * ' '
    else:
        return ' ' * pad + sep + ' ' * pad



def tabulate(text, sep, join):
    for textline in text.splitlines():
        cells = textline.split(sep)
        if len(cells) < 1:
            yield [textline.strip()]
        else:
            if join:
                yield [cell.strip() for cell in cells if cell.strip()]
            else:
                yield [cell.strip() for cell in cells]


def print_table(table, widths, pad):
    for row in table:
        out = []
        for width, cell in zip(widths, row):
            out.append(cell.ljust(width))
        print(pad.join(out).strip())


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-p', '--padding', default=1)
    parser.add_argument('-s', '--separator', default=None)
    parser.add_argument('-j', '--join-empty', action='store_true')
    args = parser.parse_args(argv[1:])

    data = sys.stdin.read()
    table = list(tabulate(data, args.separator, args.join_empty))
    pad = make_padding(args.padding, args.separator)
    widths = [max([len(cell) for cell in col])
              for col in itertools.zip_longest(*table, fillvalue='')]
    widths[-1] = 0
    print_table(table, widths, pad)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
