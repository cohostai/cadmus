#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from Queue import Empty
from time import time

from ..utils import log
from ..utils.thread import CoordinatedThread

logger = log.get_logger(__name__)


class CheckpointCommitter(CoordinatedThread):

    def __init__(self, coordinator, commit_queue, saver):
        """

        Args:
            commit_queue (Queue.Queue):
        """
        super(CheckpointCommitter, self).__init__(
            coordinator,
            name='CheckpointCommitter'
        )

        self._commit_queue = commit_queue
        self._saver = saver

    @property
    def last_commit_time(self):
        return self._saver.last_commit_time

    @property
    def last_commit_time_in_seconds(self):
        return self._saver.last_commit_time_in_seconds

    @property
    def last_checkpoint(self):
        return self._saver.last_checkpoint

    def run(self):
        self._commit_checkpoint()

    def _commit_checkpoint(self):
        while not self.should_stop():
            checkpoint = self._commit_queue.get()
            self._save_checkpoint(checkpoint)

    def _save_checkpoint(self, checkpoint):
        logger.info(
            'Save checkpoint: file `%s` | pos `%s` | schema `%s` | table `%s`',
            checkpoint.log_file,
            checkpoint.log_pos,
            checkpoint.schema,
            checkpoint.table
        )

        try:
            self._saver.save(checkpoint)
        except:
            logger.error('Cant save checkpoint. Stopping shortly...', exc_info=True)
            self.stop()


class LazyCheckpointCommitter(CheckpointCommitter):

    def __init__(self,
                 coordinator,
                 commit_queue,
                 saver,
                 commit_interval=5,
                 max_pending_checkpoints=1000):
        """

        Args:
            commit_queue (Queue.Queue):
            saver (CheckpointSaver):
            commit_interval (int): seconds
            max_pending_checkpoints (int):
        """

        super(LazyCheckpointCommitter, self).__init__(coordinator, commit_queue, saver)
        self._commit_interval = commit_interval
        self._max_pending_checkpoints = max_pending_checkpoints
        self._pending_checkpoints = 0

    def _commit_checkpoint(self):
        wait_timeout = self._commit_interval / 3.0
        checkpoint = None
        while not self.should_stop():
            try:
                checkpoint = self._commit_queue.get(timeout=wait_timeout)
                self._pending_checkpoints += 1
            except Empty:
                logger.debug('No checkpoint to commit. Should stop: %s', self.should_stop())

            if self._should_save_checkpoint() and checkpoint:
                self._save_checkpoint(checkpoint)
                self._pending_checkpoints = 0
                checkpoint = None

    def _should_save_checkpoint(self):
        current_time_in_seconds = time()

        return (
            self.last_checkpoint is None or
            self.last_commit_time is None or
            self._pending_checkpoints > self._max_pending_checkpoints or
            (current_time_in_seconds - self.last_commit_time_in_seconds) > self._commit_interval
        )
