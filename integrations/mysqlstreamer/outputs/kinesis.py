#!/usr/bin/env python
# encoding: utf-8
"""
kinesis

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import json

import boto3

from .base import EventOutput


class KinesisStreamOutput(EventOutput):

    def __init__(self,
                 coordinator,
                 pending_queue,
                 commit_queue,
                 kinesis_config):
        super(KinesisStreamOutput, self).__init__(coordinator, pending_queue)

        self.commit_queue = commit_queue
        self.kinesis_region_name = kinesis_config['region_name']
        self.kinesis_stream_name = kinesis_config['stream_name']
        self.kinesis = boto3.client(
            'kinesis',
            region_name=self.kinesis_region_name
        )

    def _output(self, envelope):
        events, checkpoint = envelope

        for event in events:
            self.kinesis.put_record(
                StreamName=self.kinesis_stream_name,
                Data=self._event_to_data(event),
                PartitionKey='default',
                SequenceNumberForOrdering=str(event['timestamp'])
            )

        self._save_checkpoint(checkpoint)

    def _save_checkpoint(self, checkpoint):
        self.commit_queue.put(checkpoint)

    @staticmethod
    def _event_to_data(event):  # TODO (thuync): support many types of serializing
        return json.dumps(event, ensure_ascii=False)
