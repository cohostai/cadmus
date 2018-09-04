#!/usr/bin/env python
# encoding: utf-8
"""
kafka

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import TopicPartition

from .base import CheckpointSaver

from ...utils import log
from ...utils.structures import BinlogCheckpoint
from ...utils.kafka.serializers import JsonSerializer
from ...utils.kafka.deserializers import JsonDeserializer

logger = log.get_logger(__name__)


class KafkaCheckpointSaver(CheckpointSaver):

    def __init__(self, bootstrap_servers, topic, **kwargs):
        super(KafkaCheckpointSaver, self).__init__()

        self._topic = topic

        self._consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id='checkpoint-saver-group',
            value_deserializer=JsonDeserializer()
        )

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            max_in_flight_requests_per_connection=1,
            retries=128,
            acks='all',
            value_serializer=JsonSerializer(),
            client_id='checkpoint-saver-client'
        )

        self.restore_checkpoint()

    def restore_checkpoint(self):
        partition = TopicPartition(self._topic, 0)
        self._consumer.assign([partition])
        self._consumer.seek_to_end()

        offset = self._consumer.position(partition)

        if not offset:
            logger.info('No checkpoint to restore.')
            return

        self._consumer.seek(partition, offset-1)
        for record in self._consumer:
            message = record.value
            self.last_commit_time = message['commit_time']
            self.last_commit_time_in_seconds = message.get(
                'commit_time_in_seconds', int(self.last_commit_time / 1000))
            self.last_checkpoint = BinlogCheckpoint(**message['checkpoint'])
            logger.info("Restore checkpoint: %s", self.last_checkpoint)
            return

    def save(self, checkpoint):

        super(KafkaCheckpointSaver, self).save(checkpoint)
        message = {
            "commit_time": self.last_commit_time,
            "commit_time_in_seconds": self.last_commit_time_in_seconds,
            "checkpoint": {
                "log_pos": self.last_checkpoint.log_pos,
                "log_file": self.last_checkpoint.log_file,
                "schema": self.last_checkpoint.schema,
                "table": self.last_checkpoint.table
            },
        }

        self._producer.send(self._topic, value=message)
