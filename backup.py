#!/usr/bin/env python

'''
Usage:
    backup [options] <source> <dest>

Options:
    --remote <server>       Remote server for ssh
    --date-format <format>  Date formats for backup folders
'''

import os
import sys
import datetime
import subprocess
import argparse
import shlex

# args to pass to rsync
RSYNC_ARGS = [
    '--archive',
    '--delete',
    '--delete-excluded',
    '--exclude-from', '/home/ingolemo/doc/backup_excludes',
    '--hard-links',
    '--human-readable',
    '--inplace',
    '--itemize-changes',
    '--numeric-ids',
    '--one-file-system',
    '--verbose',
]

# Offsets from now for which to keep a backup around
OFFSETS = {
    datetime.timedelta(hours=1),
    datetime.timedelta(hours=2),
    datetime.timedelta(hours=4),
    datetime.timedelta(hours=6),
    datetime.timedelta(hours=12),
    # days
    datetime.timedelta(days=1),
    datetime.timedelta(days=2),
    datetime.timedelta(days=4),
    datetime.timedelta(days=7),
    datetime.timedelta(days=14),
    # months
    datetime.timedelta(days=30),
    datetime.timedelta(days=30 * 2),
    datetime.timedelta(days=30 * 3),
    datetime.timedelta(days=30 * 6),
    # years
    datetime.timedelta(days=365),
    datetime.timedelta(days=365 * 2),
    datetime.timedelta(days=365 * 5),
    datetime.timedelta(days=365 * 10),
    datetime.timedelta(days=365 * 20),
    datetime.timedelta(days=365 * 50),
    datetime.timedelta(days=365 * 100),
}


def build_synccmd(source, dest, linkdest=False, remote=False):
    'builds rsync command list from arguments'
    linkd = ['--link-dest={}'.format(linkdest)] if linkdest else []
    prog = ['--progress'] if sys.stdout.isatty() else []
    if remote:
        dest = '{}:{}'.format(remote, dest)
    cmd = ['/usr/bin/rsync'] + \
        RSYNC_ARGS + linkd + prog + [source] + [dest]
    return cmd


def execute(cmd, output=False):
    print('$', *(shlex.quote(a) for a in cmd))
    if not output:
        return subprocess.call(cmd)
    else:
        out = subprocess.check_output(cmd).decode().strip()
        return out.split('\n') if out else []


def wanted_backups(all_backups, now, datefmt):
    def is_younger(folder, wanted_time):
        backup_time = datetime.datetime.strptime(
            os.path.basename(folder), datefmt)
        return backup_time > wanted_time

    wanted_time = now
    for offset in OFFSETS:
        wanted_time = now - offset
        youngers = [a for a in all_backups if is_younger(a, wanted_time)]
        if youngers:
            yield min(youngers)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--remote', default=None)
    parser.add_argument('--date-format', default='%Y_%m_%d_%H_%M_%S')
    return parser.parse_args(args[1:])


def main(argv):
    now = datetime.datetime.now()
    args = parse_args(argv)

    def make_cmd(*cmd):
        if args.remote:
            return ('ssh', args.remote) + cmd
        else:
            return cmd

    # get existing directories
    backups = execute(make_cmd(
        'find', args.destination,
        '-maxdepth', '1',
        '-mindepth', '1',
        '-type', 'd'), output=True)
    prev = max(backups, key=os.path.basename) if backups else None
    curr = os.path.join(
        args.destination, now.strftime(args.date_format))

    # create new directory
    execute(make_cmd('mkdir', curr))

    # rsync
    execute(
        build_synccmd(args.source, curr, linkdest=prev, remote=args.remote))

    # make symlink to most recent backup
    symlink_loc = os.path.join(args.destination, 'current')
    execute(make_cmd('rm', '-f', symlink_loc))
    execute(make_cmd('ln', '-s', curr, symlink_loc))

    # remove unwanted directories
    wanted = set(wanted_backups(backups, now, args.date_format))
    for backup in backups:
        if backup not in wanted:
            execute(make_cmd('rm', '-rf', backup))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
