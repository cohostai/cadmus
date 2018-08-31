#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from time import time

from ...utils.structures import BinlogCheckpoint


class CheckpointSaver(object):

    def __init__(self):
        self.last_commit_time = None
        self.last_commit_checkpoint = BinlogCheckpoint(
            log_file=None,
            log_pos=None,
            schema=None,
            table=None
        )

    def save(self, checkpoint):
        self.last_commit_time = time()
        self.last_commit_checkpoint = checkpoint
