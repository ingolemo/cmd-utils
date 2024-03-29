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

import argparse
import contextlib
import datetime
import os
import shlex
import subprocess
import sys

# args to pass to rsync
RSYNC_ARGS = {
    "--acls": None,
    "--archive": None,  # -rlptgoD
    "--delete": None,
    "--delete-excluded": None,
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
    # "--checksum": None,
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
    datetime.timedelta(hours=4),
    datetime.timedelta(hours=6),
    datetime.timedelta(hours=8),
    datetime.timedelta(hours=12),
    datetime.timedelta(hours=18),
    # days
    datetime.timedelta(days=1),
    datetime.timedelta(days=2),
    datetime.timedelta(days=4),
    datetime.timedelta(days=6),
    # weeks
    datetime.timedelta(days=7),
    datetime.timedelta(days=14),
    datetime.timedelta(days=21),
    # months
    datetime.timedelta(days=30 * 1),
    datetime.timedelta(days=30 * 2),
    datetime.timedelta(days=30 * 4),
    datetime.timedelta(days=30 * 6),
    datetime.timedelta(days=30 * 9),
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
    datetime.timedelta(days=365 * 15),
    datetime.timedelta(days=365 * 20),
    datetime.timedelta(days=365 * 50),
    datetime.timedelta(days=365 * 100),
}

LOCKFILE = ".lockfile"


def build_synccmd(source, dest, linkdests=(), remote=False, exclude_file=None):
    "builds rsync command list from arguments"
    rargs = [item for items in RSYNC_ARGS.items() for item in items if item is not None]
    if exclude_file is not None:
        rargs.append("--exclude-from")
        rargs.append(exclude_file)
    for linkdest in sorted(linkdests)[-18:]:
        rargs.extend(["--link-dest", linkdest])
    if sys.stdout.isatty():
        rargs.append("--progress")
    if remote:
        dest = "{}:{}".format(remote, dest)
    cmd = ["/usr/bin/rsync"] + rargs + [source, dest]
    return cmd


def execute(cmd, output=False, check=True):
    print("$", *(shlex.quote(a) for a in cmd))
    if output:
        out = subprocess.check_output(cmd).decode().strip()
        return out.split("\n") if out else []
    else:
        return subprocess.run(cmd, check=check).returncode


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
        "--exclude-file",
        default=os.path.join(
            os.path.expanduser(os.environ.get("XDG_CONFIG_HOME", "~/.config")),
            "backup_excludes",
        ),
        help="file containing excluded backups",
    )
    parser.add_argument(
        "--date-format",
        default="%Y-%m-%dT%H%M%S",
        help="Date format for backup folders (default: iso-8601 -ish).",
    )
    return parser.parse_args(args[1:])


@contextlib.contextmanager
def atomic_directory(make_cmd, path):
    try:
        yield
    except Exception:
        execute(make_cmd("rm", "-rf", path))
        raise


@contextlib.contextmanager
def lockfile(make_cmd, lockfile):
    if execute(make_cmd("test", "-f", lockfile), check=False) == 0:
        raise Exception(f"could not grab lock {lockfile}, exists")
    execute(make_cmd("touch", lockfile))
    try:
        yield
    finally:
        execute(make_cmd("rm", lockfile))


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
            "find",
            args.destination,
            "-maxdepth",
            "1",
            "-mindepth",
            "1",
            "-type",
            "d",
        ),
        output=True,
    )
    curr = os.path.join(args.destination, now.strftime(args.date_format))

    with lockfile(make_cmd, os.path.join(args.destination, ".lockfile")):
        # create new directory
        execute(make_cmd("mkdir", curr))

        # rsync
        with atomic_directory(make_cmd, curr):
            execute(
                build_synccmd(
                    args.source,
                    curr,
                    linkdests=backups,
                    remote=args.remote,
                    exclude_file=args.exclude_file,
                )
            )

        # make symlink to most recent backup
        symlink_loc = os.path.join(args.destination, "current")
        execute(make_cmd("rm", "-f", symlink_loc))
        execute(make_cmd("ln", "-sr", curr, symlink_loc))

        # remove unwanted directories
        wanted = set(wanted_backups(backups, now, args.date_format))
        for backup in sorted(backups, reverse=True):
            if backup not in wanted:
                execute(make_cmd("rm", "-rf", backup))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
