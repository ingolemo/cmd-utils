#!/usr/bin/env python

"""
usage: pyline <statement>

Takes a python statement as an argument and runs it for each line in
stdin. The variable `i` holds the number of the current line.

For example, this only prints even numbered lines:

    pyline 'if i%2 == 0: print(line)'

The following modules are auto-imported for ease of use:

* json
* math
* os
* subprocess
* sys
"""

import json
import math
import os
import subprocess
import sys


def main(argv):
    'main'
    for i, line in enumerate(sys.stdin):
        line = line.strip('\n')
        exec(argv[1])

if __name__ == '__main__':
    sys.exit(main(sys.argv))
