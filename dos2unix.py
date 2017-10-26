#!/usr/bin/env python
'''Usage: dos2unix <files>...

Converts the files from dos line endings to unix ones.
'''

import sys


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    for file in argv[1:]:
        with open(file, 'rb') as handle:
            content = handle.read().replace(b'\r\n', b'\n')

        with open(file, 'wb') as handle:
            handle.write(content)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
