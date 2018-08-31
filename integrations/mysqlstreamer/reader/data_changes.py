#!/usr/bin/env python
# encoding: utf-8
"""
data_changes

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from pymysqlreplication.row_event import DeleteRowsEvent
from pymysqlreplication.row_event import RowsEvent
from pymysqlreplication.row_event import UpdateRowsEvent
from pymysqlreplication.row_event import WriteRowsEvent

from ..utils.misc import miliseconds
from ..utils import log
from .base import EventConverter
from .base import QueuedBinlogReader


logger = log.get_logger(__name__)


class DataChangesEventConverter(EventConverter):

    def convert(self, row_event, slave_uuid=None):
        if isinstance(row_event, RowsEvent):
            return self._convert_row_event(row_event, slave_uuid)
        return []

    def _convert_row_event(self, row_event, slave_uuid):

        events = []

        rows = row_event.rows
        schema = row_event.schema
        table = row_event.table
        primary_key = row_event.primary_key

        logger.debug(row_event.dump())

        for row in rows:
            events.append(
                self._convert_row(
                    row_event,
                    schema, table, row, primary_key,
                    slave_uuid
                )
            )

        return events

    @staticmethod
    def _convert_row(row_event,
                     schema,
                     table,
                     row,
                     primary_key,
                     slave_uuid):
        event = {
            "slave_uuid": slave_uuid,  # where
            "timestamp": miliseconds(),  # when
            "event_type": row_event.__class__.__name__,
            "schema": schema,
            "table": table,
            "row": row,
            "primary_key": primary_key
        }

        return event


default_event_converter = DataChangesEventConverter()


class DataChangesBinlogReader(QueuedBinlogReader):

    def __init__(self,
                 coordinator,
                 connection_settings,
                 server_id,
                 log_file,
                 log_pos,
                 pending_queue,
                 event_converter=default_event_converter,
                 **kwargs):
        """

        Args:
            pending_queue (Queue.Queue):
            event_converter (EventConverter):
        """
        super(DataChangesBinlogReader, self).__init__(
            coordinator,
            connection_settings,
            server_id,
            log_file,
            log_pos,
            pending_queue,
            event_converter,
            only_events=[WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent],
            **kwargs
        )
