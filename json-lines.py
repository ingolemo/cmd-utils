#!/usr/bin/env python
"""Takes a pipeline and converts it to a json array — one entry for each line.
"""

import json
import sys


def main(argv):
    if "-h" in argv or "--help" in argv:
        return __doc__

    lines = json.dumps([line.rstrip("\n") for line in sys.stdin.readlines()])
    sys.stdout.write(lines)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
