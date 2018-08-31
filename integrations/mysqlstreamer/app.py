#!/usr/bin/env python
# encoding: utf-8
"""
main

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import time
import sys
from Queue import Queue

from integrations.mysqlstreamer.utils.thread.coordinator import Coordinator
from .committers import LazyCheckpointCommitter
from .committers.savers import DynamoCheckpointSaver
from .outputs import KinesisStreamOutput
from .reader import DataChangesBinlogReader

from .utils import log

logger = log.get_logger(__name__)


class App(object):
    """
    Attributes:
        pending_queue:
        commit_queue:
        committer:
        binlog_reader:
        outputer:
    """

    def __init__(self, config):
        self.config = config
        self.coordinator = Coordinator()

        self.pending_queue = None
        self.commit_queue = None
        self.committer = None
        self.binlog_reader = None
        self.outputer = None

        self.setup_app()

    def setup_app(self):
        self.pending_queue = Queue()
        self.commit_queue = Queue()

        self.setup_checkpoint_committer()
        self.setup_binlog_reader()
        self.setup_outputer()

    def start(self):
        self.binlog_reader.start()
        self.outputer.start()
        self.committer.start()

        self.outputer.join()
        self.committer.join()
        self.binlog_reader.join()

    def stop(self):
        self.coordinator.stop()

    def setup_outputer(self):
        kinesis_config = {
            'stream_name': self.config.KINESIS_STREAM_NAME,
            'region_name': self.config.KINESIS_REGION_NAME,
        }
        self.outputer = KinesisStreamOutput(
            self.coordinator,
            self.pending_queue,
            self.commit_queue,
            kinesis_config=kinesis_config
        )

    def setup_binlog_reader(self):
        connection_settings = {
            "host": self.config.MYSQL_MASTER_HOST,
            "port": self.config.MYSQL_MASTER_PORT,
            "user": self.config.MYSQL_USER,
            "passwd": self.config.MYSQL_PASSWD
        }

        last_checkpoint = self.committer.last_commit_checkpoint

        self.binlog_reader = DataChangesBinlogReader(
            self.coordinator,
            connection_settings,
            self.config.SERVER_ID,
            log_file=last_checkpoint.log_file,
            log_pos=last_checkpoint.log_pos,
            pending_queue=self.pending_queue,
        )

    def setup_checkpoint_committer(self):
        checkpoint_saver = DynamoCheckpointSaver(
            self.config.DYNAMO_CHECKPOINT_TABLE,
            self.config.DYNAMO_REGION_NAME
        )

        self.committer = LazyCheckpointCommitter(
            self.coordinator,
            self.commit_queue,
            checkpoint_saver,
            self.config.COMMIT_INTERVAL,
            self.config.MAX_PENDING_CHECKPOINTS
        )
