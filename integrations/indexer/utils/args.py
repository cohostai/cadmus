#!/usr/bin/env python
# encoding: utf-8
"""
args

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from collections import Iterable


def arg_or_iter(arg):
    if isinstance(arg, (list, tuple, set)):
        return arg
    else:
        return [arg]
