#!/usr/bin/env python
# encoding: utf-8
"""
config

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals


KAFKA_BOOTSTRAP_SERVERS = ['13.112.90.56:9290']
KAFKA_CONSUMER_GROUP = 'indexer-group'
KAFKA_EVENT_TOPIC = 'mysqlstreamer_events'

ELASTICSEARCH_HOSTS = 'localhost:9200'

BATCH_SIZE = 0
