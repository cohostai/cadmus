#!/usr/bin/env python
# encoding: utf-8
"""
checkpoint

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals


from collections import namedtuple

BinlogCheckpoint = namedtuple(
    'BinlogCheckpoint',
    ['log_file', 'log_pos', 'schema', 'table']
)

Envelope = namedtuple(
    'Envelope',
    ['events', 'checkpoint']
)
