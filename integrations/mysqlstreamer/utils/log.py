#!/usr/bin/env python
# encoding: utf-8
"""
log

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)


def get_logger(name):
    return logging.getLogger(name)
