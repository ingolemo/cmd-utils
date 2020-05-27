#!/usr/bin/env python
"""Usage: countdown [hours]h[minutes]m[seconds]s

Takes a time specifier and counts down that amount of time, exiting
once the time has expired. Like `sleep`, but with a progress counter
and takes times in a more human readable format.

The time should be given with a number followed by a letter indicating
the period. More than one time period can be given at once. If a number
is given, but no letter then m (minutes) is assumed. Examples:

    countdown 3m                (3 minutes)
    countdown 10                (10 minutes)
    countdown 1h                (1 hour)
    countdown 9h30m             (9 and a half hours)
    countdown 1h30              (1 hour and 30 minutes)
    countdown 1h30s             (1 hour and 30 seconds)
"""

import datetime
import re
import sys
import time


def parse(args):
    arg = args[1]
    regex = r"((?P<h>[0-9]+)h)?((?P<m>[0-9]+)m?)??((?P<s>[0-9]+)s)?"
    match = re.fullmatch(regex, arg)
    if not match:
        raise ValueError("cannot parse string")
    d = match.groupdict()

    times = [d.get(a, 0) or 0 for a in "hms"]
    h, m, s = [int(a) for a in times]
    return datetime.timedelta(seconds=(h * 60 + m) * 60 + s)


def format_delta(delta):
    total_minutes, seconds = divmod(delta.total_seconds(), 60)
    total_hours, minutes = divmod(total_minutes, 60)
    return f"{int(total_hours):02}:{int(minutes):02}:{int(seconds):02}"


def main(argv):
    if "-h" in argv or "--help" in argv:
        return __doc__

    try:
        length = parse(argv)
    except (IndexError, ValueError):
        return __doc__
    start = datetime.datetime.now()
    finish = start + length

    while True:
        now = datetime.datetime.now()
        left = finish - now
        print(format_delta(left), end="\r")
        if now > finish:
            break
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
