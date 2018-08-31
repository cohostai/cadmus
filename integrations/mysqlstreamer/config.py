#!/usr/bin/env python
# encoding: utf-8
"""
config

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

SERVER_ID = 100

DYNAMO_CHECKPOINT_TABLE = 'chocon-mysqlreplication'
DYNAMO_REGION_NAME = 'ap-northeast-1'

KINESIS_REGION_NAME = 'ap-northeast-1'
KINESIS_STREAM_NAME = 'OnlineFriday_Popup'

COMMIT_INTERVAL = 5
MAX_PENDING_CHECKPOINTS = 1000

MYSQL_MASTER_HOST = 'chocon-cluster-dev.cluster-csiquhqyczzd.ap-northeast-1.rds.amazonaws.com'
MYSQL_MASTER_PORT = 6303
MYSQL_USER = 'conan'
MYSQL_PASSWD = 'ShAwpgSxX3JB3ZRy'
