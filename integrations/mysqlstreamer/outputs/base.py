#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from Queue import Empty

from ..utils.thread import CoordinatedThread
from ..utils import log

logger = log.get_logger(__name__)


class EventOutput(CoordinatedThread):

    def __init__(self, coordinator, pending_queue, *args, **kwargs):
        """

        Args:
            pending_queue (Queue.Queue):
            commit_queue (Queue.Queue):
        """
        super(EventOutput, self).__init__(coordinator, name='EventOutput')
        self._pending_queue = pending_queue

    def run(self):
        while not self.should_stop():
            try:
                events, checkpoint = self._pending_queue.get(timeout=5)
                self._output(checkpoint, events)
            except Empty:
                logger.debug('No event to output. Should stop: %s', self.should_stop())
                continue
            except:
                logger.error("Cant output event. Stopping shortly...", exc_info=True)
                self.stop()

    def _output(self, checkpoint, events):
        raise NotImplementedError

