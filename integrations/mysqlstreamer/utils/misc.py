#!/usr/bin/env python
# encoding: utf-8
"""
utils

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from time import time


def miliseconds():
    return int(time() * 1000)


def seconds():
    return int(time())

