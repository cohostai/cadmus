#!/usr/bin/env sh

set -e

gunicorn cadmus -b 0.0.0.0:7111 -w 3 -k gevent --name cadmus --timeout 120