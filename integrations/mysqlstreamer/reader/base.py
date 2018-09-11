#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from pymysqlreplication import BinLogStreamReader

from ..utils.structures import Envelope
from ..utils.structures import BinlogCheckpoint
from ..utils import log
from ..utils.thread import CoordinatedThread


logger = log.get_logger(__name__)


class BinlogReader(CoordinatedThread):

    def __init__(self,
                 coordinator,
                 connection_settings,
                 server_id,
                 log_file,
                 log_pos,
                 **kwargs):
        """

        Args:
            stream (BinLogStreamReader):
        """
        super(BinlogReader, self).__init__(
            coordinator,
            name='BinlogReader'
        )

        self._stream = BinLogStreamReader(
            connection_settings,
            server_id=server_id,
            blocking=True,
            resume_stream=True,
            log_file=log_file,
            log_pos=log_pos,
            **kwargs
        )

    def run(self):
        logger.info('Reading binlog stream...')
        for binlogevent in self._stream:
            self._handle_binlogevent(binlogevent)

            if self.should_stop():
                break

    def _handle_binlogevent(self, binlogevent):
        """

        Args:
            binlogevent:

        Returns:

        """
        raise NotImplementedError


class QueuedBinlogReader(BinlogReader):

    def __init__(self,
                 coordinator,
                 connection_settings,
                 server_id,
                 log_file,
                 log_pos,
                 pending_queue,
                 event_convert,
                 **kwargs):

        super(QueuedBinlogReader, self).__init__(
            coordinator,
            connection_settings,
            server_id,
            log_file,
            log_pos,
            **kwargs
        )

        self._pending_queue = pending_queue
        self._event_converter = event_convert

    def _handle_binlogevent(self, binlogevent):
        """

        Args:
            binlogevent (RowsEvent):

        Returns:

        """

        events = self._event_converter.convert(
            binlogevent,
            slave_uuid=self._stream.slave_uuid
        )

        checkpoint = BinlogCheckpoint(
            log_file=self._stream.log_file,
            log_pos=self._stream.log_pos,
            schema=binlogevent.schema,
            table=binlogevent.table
        )

        envelope = Envelope(
            events=events,
            checkpoint=checkpoint
        )

        self._pending_queue.put(envelope)


class EventConverter(object):
    """
    Convert binlogevent to other events.
    """

    def convert(self, binlogevent, **kwargs):
        raise NotImplementedError

