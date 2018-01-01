#!/usr/bin/env python
'''Usage: sponge <file>

Collects stdin and waits for it to close before opening the file and
writing everything it has collected. This is useful when other parts of
the pipeline are using the file because opening a file blanks it out.
'''

import sys


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    output = [line for line in sys.stdin.buffer]
    with open(argv[1], 'wb') as file:
        for bytes in output:
            file.write(bytes)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
