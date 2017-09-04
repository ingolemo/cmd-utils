#!/usr/bin/env python

import collections
import functools
import logging
import pathlib
import string
import sys
import random

import docopt

__doc__ = '''
Usage:
    symtag init <base>
    symtag add <base> <files>...
    symtag rm <base> <files>...
    symtag tag <base> <file> <tags>...
    symtag ls <base> [<tags>...]
    symtag leasttagged <base>
    symtag listalltags <base>
    symtag listtags <base> <file>

Symtag is a symlink based database. <base> should be a directory that
is the base of the database.
'''

logging.basicConfig(
    format='%(message)s', level=logging.INFO, stream=sys.stderr
)


class Database:
    def __init__(self, base, init=False):
        self.base = pathlib.Path(base)
        self.tagbase = self.base.joinpath('tags')
        self.filebase = self.base.joinpath('files')
        self.dotfile = self.base.joinpath('.symtag.conf')

        if init:
            self.tagbase.mkdir(parents=True)
            self.filebase.mkdir(parents=True)
            self.dotfile.touch()

        if not self.dotfile.is_file():
            raise ValueError('Database {} is invalid'.format(self.base))

        self.base = self.base.resolve()
        self.tagbase = self.tagbase.resolve()
        self.filebase = self.filebase.resolve()
        self.dotfile = self.dotfile.resolve()

    def _get_tagdir(self, tag, ensure_exists=False):
        'Converts a tag into a tag directory, optionally creating it'
        if not self.is_valid_tag(tag):
            raise ValueError('Invalid tag "{}"'.format(tag))
        tagdir = self.tagbase.joinpath(tag)
        if ensure_exists:
            try:
                tagdir.mkdir()
            except FileExistsError:
                pass
            else:
                logging.info('Created new tag "{}"'.format(tag))
        return tagdir

    def _get_taglink(self, tag, file, make_tag=False):
        tagdir = self._get_tagdir(tag, make_tag)
        taglink = tagdir.joinpath(file.name)
        return taglink

    def is_valid_file(self, file):
        'Returns if file is in the database'
        try:
            file = file.resolve()
            file.relative_to(self.filebase)
            if file.is_dir():
                raise ValueError('{} is directory'.format(file))
            if file.is_symlink():
                raise ValueError('{} is symlink'.format(file))
        except ValueError:
            return False
        return True

    def is_valid_tag(self, tag):
        valid_chars = string.ascii_lowercase + string.digits + '_'
        return all(a in valid_chars for a in tag)

    def is_valid_taglink(self, taglink):
        'Returns if a tag file is valid'
        if not taglink.exists():
            return False
        if not taglink.is_symlink():
            logging.warning('{} is not a symlink'.format(taglink))
            return False
        return True

    def is_valid_tag_to(self, file, tag):
        'Returns whether a file has a particular tag'
        taglink = self._get_taglink(tag, file)
        if not self.is_valid_taglink(taglink):
            return False
        if taglink.resolve() != file.resolve():
            logging.warning('Tag does not link to file')
            return False
        return True

    def query(self, query_str):
        whitelist, blacklist = parse_tag_changes(query_str.split())
        files = set(self.all_files())
        for tag in whitelist:
            require = set(self.files_with_tag(tag))
            files = files & require
        for tag in blacklist:
            exclude = set(self.files_with_tag(tag))
            files = files - exclude
        return files

    def add_file(self, file):
        dest = self.base.joinpath('files', file.name)
        if dest.exists():
            logging.info('{} already exists'.format(dest.name))
            return
        logging.info('Adding {}'.format(file))
        copy_file(file, dest)

    def remove_file(self, file):
        if not self.is_valid_file(file):
            raise ValueError('{} not in database'.format(file))
        for tag in self.tags_on_file(file):
            self.remove_tag(file, tag)
        logging.info('Removing file {}'.format(file.name))
        file.unlink()

    def add_tag(self, file, tag):
        taglink = self._get_taglink(tag, file, make_tag=True)
        try:
            taglink.symlink_to(file)
        except FileExistsError:
            logging.info('{} already tagged {}'.format(file.name, tag))
        else:
            logging.info('Added {} to {}'.format(tag, file.name))

    def remove_tag(self, file, tag):
        taglink = self._get_taglink(tag, file)
        try:
            taglink.unlink()
        except FileNotFoundError:
            logging.info('{} not tagged {}'.format(file.name, tag))
        else:
            logging.info('Removed {} from {}'.format(tag, file.name))

        # if tag is completely empty remove it
        if not self.files_with_tag(tag):
            tagdir = self._get_tagdir(tag)
            tagdir.rmdir()

    @functools.lru_cache()
    def files_with_tag(self, tag):
        result = []
        for file in self._get_tagdir(tag).iterdir():
            file = file.resolve()
            if self.is_valid_tag_to(file, tag):
                result.append(file)
        return result

    @functools.lru_cache()
    def tags_on_file(self, file):
        result = []
        file = file.resolve()
        for tag in self.all_tags():
            if self.is_valid_tag_to(file, tag):
                result.append(tag)
        return result

    def all_files(self):
        for file in self.filebase.iterdir():
            yield file.resolve()

    def all_tags(self):
        for tagdir in self.tagbase.iterdir():
            yield tagdir.name


def load_file(fname):
    return pathlib.Path(fname).resolve()


def parse_tag_changes(tags):
    plus, minus = set(), set()
    for tag in tags:
        bag = minus if tag.endswith('-') else plus
        bag.add(tag.rstrip('+-'))
    return plus, minus


def copy_file(source, dest):
    with source.open('rb') as source_fd:
        with dest.open('wb') as dest_fd:
            dest_fd.write(source_fd.read())


def action_addfiles(db, args):
    for fname in args['<files>']:
        source = load_file(fname)
        db.add_file(source)


def action_rmfiles(db, args):
    for fname in args['<files>']:
        file = load_file(fname)
        db.remove_file(file)


def action_tagfile(db, args):
    dest = load_file(args['<file>'])
    plus, minus = parse_tag_changes(args['<tags>'])
    for tag in plus:
        db.add_tag(dest, tag)
    for tag in minus:
        db.remove_tag(dest, tag)


def action_listfiles(db, args):
    tags = ' '.join(args['<tags>'])
    for file in db.query(tags):
        print(file)


def action_listalltags(db, args):
    for tag in db.all_tags():
        print(tag)


def action_listtags(db, args):
    file = load_file(args['<file>'])
    tags = db.tags_on_file(file)
    print(' '.join(sorted(tags)))


def action_leasttagged(db, args):
    numtags = lambda f: len(set(db.tags_on_file(f)))
    #return min(db.all_files(), key=numtags)
    lowest = 10000000, None
    for file in sorted(db.all_files(), key=lambda a: random.random()):
        n = numtags(file)
        if n < lowest[0]:
            lowest = n, file
        if n <= 0:
            break
    file = lowest[1]
    print(file)


def main(args):
    args = docopt.docopt(__doc__)
    db = Database(args['<base>'], init=args['init'])
    cmds = {
        'init': lambda *args: None,
        'add': action_addfiles,
        'rm': action_rmfiles,
        'tag': action_tagfile,
        'ls': action_listfiles,
        'leasttagged': action_leasttagged,
        'listalltags': action_listalltags,
        'listtags': action_listtags,
    }
    for cmd, func in cmds.items():
        if not args.get(cmd):
            continue

        return func(db, args)
    print(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
