#!/usr/bin/env python
"""
Usage: chronic <program> [args]...

Runs a program, capturing its stdout and stderr, and only outputs it if
the program fails (i.e. the program returns a non-zero return code or
writes anything at all to stderr).

The stdio will also be written to a log file in `~/.cache/chronic`
for debugging purposes, regardless whether it failed or not.

Useful for running processes under cron.
"""

from subprocess import PIPE
import datetime
import fcntl
import os
import pathlib
import subprocess
import sys
import time


def set_nonblocking(fileobject):
    "Sets a fileobject to non-blocking mode"
    descriptor = fileobject.fileno()
    flags = fcntl.fcntl(descriptor, fcntl.F_GETFL)
    fcntl.fcntl(descriptor, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def get_logfile(cmd):
    "Converts a command list to a valid file name for the log."
    replacements = {'/': '7', ' ': '_', '$': 'S', '"': '', '&': '8'}
    sanitised = '_'.join(cmd)
    for key, value in replacements.items():
        sanitised = sanitised.replace(key, value)
    return '{}.log'.format(sanitised)


def run_cmd(cmd, logfile):
    "Runs a cmd list, capturing and logging stdio."
    proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1)
    with open(logfile, 'w') as log:
        log.write('run {}\n'.format(cmd))
        log.write('\tat {}\n\n'.format(datetime.datetime.now()))
        log.flush()
        output = list(await_proc(proc, log))
    return proc.returncode, output


def await_proc(proc, log):
    "Processes a proc, capturing and logging stdio."
    set_nonblocking(proc.stdout)
    set_nonblocking(proc.stderr)

    running = True
    while running:
        if proc.poll() is None:
            time.sleep(0.1)
        else:
            running = False

        out = proc.stdout.read()
        err = proc.stderr.read()
        if out:
            outt = out.decode()
            log.write(outt)
            log.flush()
            yield False, outt
        if err:
            errt = err.decode()
            log.write(errt)
            log.flush()
            yield True, errt


def xdg_cache_dir(name):
    default = pathlib.Path('~/.cache').expanduser()
    base = pathlib.Path(os.environ.get('XDG_CACHE_HOME', default))
    fname = base / name
    if not fname.exists():
        fname.mkdir()
    return fname


def main(argv):
    if not argv[1:] or '-h' in argv or '--help' in argv:
        return __doc__

    cmd = argv[1:]
    logfile = os.path.join(xdg_cache_dir('chronic'), get_logfile(cmd))
    retcode, output = run_cmd(cmd, logfile)
    uses_stderr = any(is_err for is_err, string in output)

    if retcode != 0 or uses_stderr:
        for is_err, string in output:
            std = sys.stderr if is_err else sys.stdout
            print(string.rstrip('\n'), file=std)

    return retcode


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        pass
