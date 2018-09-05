#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals


from elasticsearch import helpers

from ..utils.args import arg_or_iter
from ..utils import log

logger = log.get_logger(__name__)


def is_rows_event(event):
    event_type = event.get('event_type')
    if event_type and 'RowsEvent' in event_type:
        return True
    else:
        return False


class Indexer(object):

    def __init__(self, client, index_by_table, index_creator, row_processor):
        self._client = client
        self._index_creator = index_creator
        self._row_processor = row_processor
        self._index_by_table = index_by_table

        self._index_creator.create()

    def process(self, event_or_events):
        actions = self._build_actions(event_or_events)

        if not actions:
            return
        _, errors = helpers.bulk(self._client, actions, max_retries=128)
        if errors:
            raise Exception('Some errors occurred: %s', errors)

    def _build_actions(self, events):
        events = arg_or_iter(events)
        events = [ev for ev in events if is_rows_event(ev)]
        actions = []
        for event in events:
            try:
                action = self._build_action(event)
                actions.append(action)
            except Exception as e:
                logger.warn('Cant build action for event \n'
                            '%s\n'
                            'caused by %s', event, e)

        return actions

    def _get_index_name(self, event):
        table_name = "{schema}.{table}".format(
            schema=event["schema"],
            table=event["table"]
        )

        index_name = self._index_by_table.get(table_name)
        if not index_name:
            raise Exception('Cant find index name for table: %s' % table_name)

        return index_name

    def _build_action(self, event):

        index_name = self._get_index_name(event)
        doc = self._row_processor.process(
            event["schema"],
            event["table"],
            event["row"]
        )
        doc_id = doc[event["primary_key"]]

        if event["event_type"] in ["UpdateRowsEvent", "WriteRowsEvent"]:
            action = {
                "_op_type": "update",
                "_index": index_name,
                "_type": "_doc",
                "_id": doc_id,
                "_source": {
                    "doc": doc,
                    "doc_as_upsert": True
                }
            }
        elif event["event_type"] in ["DeleteRowsEvent"]:
            action = {
                "_op_type": "delete",
                "_index": index_name,
                "_type": "_doc",
                "_id": doc_id
            }
        else:
            raise Exception("Invalid event type: %s", event)

        return action
