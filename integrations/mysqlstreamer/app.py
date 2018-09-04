#!/usr/bin/env python
# encoding: utf-8
"""
main

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from Queue import Queue

from integrations.mysqlstreamer.utils.thread.coordinator import Coordinator

from .committers import LazyCheckpointCommitter
from .committers.savers import KafkaCheckpointSaver
from .outputs import KafkaEventOutput
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

    def stop(self):
        self.coordinator.stop()
        self.outputer.join()
        self.committer.join()

    def should_stop(self):
        return self.coordinator.should_stop()

    def setup_outputer(self):

        self.outputer = KafkaEventOutput(
            self.coordinator,
            self.pending_queue,
            self.commit_queue,
            bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
            topic=self.config.KAFKA_EVENT_TOPIC
        )

    def setup_binlog_reader(self):
        connection_settings = {
            "host": self.config.MYSQL_MASTER_HOST,
            "port": self.config.MYSQL_MASTER_PORT,
            "user": self.config.MYSQL_USER,
            "passwd": self.config.MYSQL_PASSWD
        }

        last_checkpoint = self.committer.last_checkpoint

        self.binlog_reader = DataChangesBinlogReader(
            self.coordinator,
            connection_settings,
            self.config.SERVER_ID,
            log_file=last_checkpoint.log_file,
            log_pos=last_checkpoint.log_pos,
            pending_queue=self.pending_queue,
        )

    def setup_checkpoint_committer(self):
        checkpoint_saver = KafkaCheckpointSaver(
            self.config.KAFKA_BOOTSTRAP_SERVERS,
            self.config.KAFKA_COMMIT_TOPIC,
        )

        self.committer = LazyCheckpointCommitter(
            self.coordinator,
            self.commit_queue,
            checkpoint_saver,
            self.config.COMMIT_INTERVAL,
            self.config.MAX_PENDING_CHECKPOINTS
        )
