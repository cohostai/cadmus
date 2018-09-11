#!/usr/bin/env python
# encoding: utf-8
"""
kafka

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata

from ..utils import log
from ..utils.kafka.serializers import JsonSerializer
from .base import EventOutput

logger = log.get_logger(__name__)


class KafkaEventOutput(EventOutput):

    # TODO(thuync): add event output stats

    def __init__(self,
                 coordinator,
                 pending_queue,
                 commit_queue,
                 bootstrap_servers,
                 topic,
                 **kwargs):
        super(KafkaEventOutput, self).__init__(coordinator, pending_queue)
        self._commit_queue = commit_queue

        self._bootstrap_servers = bootstrap_servers
        self._topic = topic

        # TODO(thuync): Read more about producer params
        self._producer = KafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            max_in_flight_requests_per_connection=1,
            retries=128,
            acks='all',
            value_serializer=JsonSerializer(),
            client_id='KafkaEventOutput'
        )

    def _publish_event(self, event):
        return self._producer.send(  # async
            self._topic,
            value=event,
            key=None,
            partition=None,
            timestamp_ms=None
        )

    def _output(self, checkpoint, events):
        futures = [
            self._publish_event(event)
            for event in events
        ]

        if futures:  # TODO(thuync): only consider last future?
            last_future = futures[-1]  # type: FutureRecordMetadata
            last_future.add_callback(self._on_publish_success, checkpoint)\
                .add_errback(self._on_publish_error, checkpoint)

    def _on_publish_success(self, checkpoint, metadata):
        logger.info('Commit checkpoint: %s', checkpoint)
        self._commit_queue.put(checkpoint)

    def _on_publish_error(self, checkpoint, exception):
        logger.error('Failed to publish event : %s | %s', checkpoint, exception)
        self.stop()
