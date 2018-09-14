#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

import hashlib


def to_list(s, delimiter=',', subcast=None, raise_on_error=False):
    try:
        es = s.split(delimiter)
        if subcast and callable(subcast):
            es = [subcast(e) for e in es]
        return es
    except:  # noqa
        if raise_on_error:
            raise
        return []


def to_int(s, raise_on_error=False, default=0):
    try:
        return int(s.strip())
    except:  # noqa
        if raise_on_error:
            raise
        return default


def to_bool(s, raise_on_error=False, default=False):
    try:
        if s.lower() in ['f', 'false']:
            return False
        elif s.lower() in ['t', 'true']:
            return True
        else:
            return default
    except:  # noqa
        if raise_on_error:
            raise

        return default


def hash_str(var_str):
    if not var_str:
        return None

    return hashlib.sha256(var_str.encode('utf-8')).hexdigest()
