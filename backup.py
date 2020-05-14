#!/usr/bin/env python
# see `backup --help` for full options
"""
Make a backup of the source directory to the destination using
rsync. Creates a directory in the destination with the date that the
backup was made. If the destination contains previous backups then the
new backup will be done incrementally using the --link-dest feature of
rsync to create hardlinks to files that have not changed. It will also
delete backups that are too old using a sort of exponential backoff to
keep fewer backups as they go further into the past.
"""

import os
import sys
import datetime
import subprocess
import argparse
import shlex

excludes = os.path.join(
    os.path.expanduser(os.environ.get("XDG_CONFIG_HOME", "~/.config")),
    "backup_excludes",
)

# args to pass to rsync
RSYNC_ARGS = {
    "--acls": None,
    "--archive": None,  # -rlptgoD
    "--delete": None,
    "--delete-excluded": None,
    "--exclude-from": excludes,
    "--hard-links": None,
    "--human-readable": None,
    "--inplace": None,
    "--itemize-changes": None,
    "--max-size": "2g",
    "--numeric-ids": None,
    "--one-file-system": None,
    "--preallocate": None,
    "--relative": None,
    "--verbose": None,
    "--xattrs": None,
}

# Offsets from now for which to keep a backup around
OFFSETS = {
    # minutes
    datetime.timedelta(minutes=1),
    datetime.timedelta(minutes=2),
    datetime.timedelta(minutes=5),
    datetime.timedelta(minutes=10),
    datetime.timedelta(minutes=20),
    datetime.timedelta(minutes=30),
    # hours
    datetime.timedelta(hours=1),
    datetime.timedelta(hours=2),
    datetime.timedelta(hours=3),
    datetime.timedelta(hours=4),
    datetime.timedelta(hours=5),
    datetime.timedelta(hours=6),
    datetime.timedelta(hours=7),
    datetime.timedelta(hours=8),
    datetime.timedelta(hours=9),
    datetime.timedelta(hours=10),
    datetime.timedelta(hours=12),
    datetime.timedelta(hours=14),
    datetime.timedelta(hours=16),
    datetime.timedelta(hours=18),
    datetime.timedelta(hours=20),
    datetime.timedelta(hours=22),
    # days
    datetime.timedelta(days=1),
    datetime.timedelta(days=2),
    datetime.timedelta(days=3),
    datetime.timedelta(days=4),
    datetime.timedelta(days=5),
    datetime.timedelta(days=6),
    datetime.timedelta(days=7),
    datetime.timedelta(days=14),
    datetime.timedelta(days=21),
    # months
    datetime.timedelta(days=30 * 1),
    datetime.timedelta(days=30 * 2),
    datetime.timedelta(days=30 * 3),
    datetime.timedelta(days=30 * 4),
    datetime.timedelta(days=30 * 5),
    datetime.timedelta(days=30 * 6),
    datetime.timedelta(days=30 * 7),
    datetime.timedelta(days=30 * 8),
    datetime.timedelta(days=30 * 9),
    datetime.timedelta(days=30 * 10),
    datetime.timedelta(days=30 * 11),
    # years
    datetime.timedelta(days=365 * 1),
    datetime.timedelta(days=365 * 2),
    datetime.timedelta(days=365 * 3),
    datetime.timedelta(days=365 * 4),
    datetime.timedelta(days=365 * 5),
    datetime.timedelta(days=365 * 6),
    datetime.timedelta(days=365 * 7),
    datetime.timedelta(days=365 * 8),
    datetime.timedelta(days=365 * 9),
    datetime.timedelta(days=365 * 10),
    datetime.timedelta(days=365 * 12),
    datetime.timedelta(days=365 * 14),
    datetime.timedelta(days=365 * 16),
    datetime.timedelta(days=365 * 18),
    datetime.timedelta(days=365 * 20),
    datetime.timedelta(days=365 * 30),
    datetime.timedelta(days=365 * 40),
    datetime.timedelta(days=365 * 50),
    datetime.timedelta(days=365 * 60),
    datetime.timedelta(days=365 * 70),
    datetime.timedelta(days=365 * 80),
    datetime.timedelta(days=365 * 90),
    datetime.timedelta(days=365 * 100),
}


def build_synccmd(source, dest, linkdests=(), remote=False):
    "builds rsync command list from arguments"
    rargs = [item for items in RSYNC_ARGS.items() for item in items if item is not None]
    for linkdest in sorted(linkdests)[-18:]:
        rargs.extend(["--link-dest", linkdest])
    if sys.stdout.isatty():
        rargs.append('--progress')
    if remote:
        dest = "{}:{}".format(remote, dest)
    cmd = ["/usr/bin/rsync"] + rargs + [source, dest]
    return cmd


def execute(cmd, output=False):
    print("$", *(shlex.quote(a) for a in cmd))
    if not output:
        return subprocess.run(cmd, check=True).returncode
    else:
        out = subprocess.check_output(cmd).decode().strip()
        return out.split("\n") if out else []


def wanted_backups(all_backups, now, datefmt):
    def is_younger(folder, wanted_time):
        backup_time = datetime.datetime.strptime(os.path.basename(folder), datefmt)
        return backup_time > wanted_time

    wanted_time = now
    for offset in OFFSETS:
        wanted_time = now - offset
        youngers = [a for a in all_backups if is_younger(a, wanted_time)]
        if youngers:
            yield min(youngers)


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--remote", default=None, help="remote server for ssh")
    parser.add_argument(
        "--date-format",
        default="%Y-%m-%dT%H%M%S",
        help="Date format for backup folders (default: iso-8601 -ish).",
    )
    return parser.parse_args(args[1:])


def main(argv):
    now = datetime.datetime.now()
    args = parse_args(argv)

    def make_cmd(*cmd):
        if args.remote:
            return ("ssh", args.remote) + cmd
        else:
            return cmd

    # get existing directories
    backups = execute(
        make_cmd(
            "find", args.destination, "-maxdepth", "1", "-mindepth", "1", "-type", "d",
        ),
        output=True,
    )
    curr = os.path.join(args.destination, now.strftime(args.date_format))

    # create new directory
    execute(make_cmd("mkdir", curr))

    # rsync
    execute(build_synccmd(args.source, curr, linkdests=backups, remote=args.remote))

    # make symlink to most recent backup
    symlink_loc = os.path.join(args.destination, "current")
    execute(make_cmd("rm", "-f", symlink_loc))
    execute(make_cmd("ln", "-sr", curr, symlink_loc))

    # remove unwanted directories
    wanted = set(wanted_backups(backups, now, args.date_format))
    for backup in backups:
        if backup not in wanted:
            execute(make_cmd("rm", "-rf", backup))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
