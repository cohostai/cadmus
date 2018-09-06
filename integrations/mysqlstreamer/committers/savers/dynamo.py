#!/usr/bin/env python
# encoding: utf-8
"""
dynamo

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import boto3
from .base import CheckpointSaver
from ...utils.misc import miliseconds
from ...utils.structures import BinlogCheckpoint


class DynamoCheckpointSaver(CheckpointSaver):

    def __init__(self, table_name, region_name):
        super(DynamoCheckpointSaver, self).__init__()
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.restore_checkpoint()

    def restore_checkpoint(self):
        result = self.table.get_item(
            Key={
                "key": "binlog-checkpoint"
            }
        )

        if "Item" in result:
            item = result["Item"]
            self.last_commit_time = item["commit_time"]
            self.last_checkpoint = BinlogCheckpoint(
                **item["checkpoint"]
            )

    def save(self, checkpoint):
        super(DynamoCheckpointSaver, self).save(checkpoint)

        item = {
            "commit_time": self.last_commit_time,
            "checkpoint": {
                "log_file": self.last_checkpoint.log_file,
                "log_pos": self.last_checkpoint.log_pos,
                "schema": self.last_checkpoint.schema,
                "table": self.last_checkpoint.table,
            },
            "key": "binlog-checkpoint"
        }

        self.table.put_item(Item=item)
