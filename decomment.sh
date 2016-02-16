#!/usr/bin/env sh
exec awk '$0 !~ /^(\w*#.*)?$/'
