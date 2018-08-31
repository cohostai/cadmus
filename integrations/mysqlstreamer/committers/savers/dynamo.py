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
            self.last_commit_checkpoint = BinlogCheckpoint(
                **item["checkpoint"]
            )

    def save(self, checkpoint):
        item = {
            "commit_time": miliseconds(),
            "checkpoint": {
                "log_file": checkpoint.log_file,
                "log_pos": checkpoint.log_pos,
                "schema": checkpoint.schema,
                "table": checkpoint.table,
            },
            "key": "binlog-checkpoint"
        }

        self.table.put_item(Item=item)
