#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ...utils.structures import BinlogCheckpoint
from ...utils.misc import miliseconds
from ...utils.misc import seconds


class CheckpointSaver(object):
    """
    Attributes:
        last_commit_time (int):
        last_commit_time_in_seconds (int):
        last_checkpoint (BinlogCheckpoint):
    """

    default_checkpoint = BinlogCheckpoint(log_file=None,
                                          log_pos=None,
                                          schema=None,
                                          table=None)

    def __init__(self):
        self.last_commit_time = miliseconds()
        self.last_commit_time_in_seconds = seconds()
        self.last_checkpoint = self.default_checkpoint

    def save(self, checkpoint):
        self.last_commit_time = miliseconds()
        self.last_commit_time_in_seconds = seconds()
        self.last_checkpoint = checkpoint
