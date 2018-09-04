#!/usr/bin/env python
# encoding: utf-8
"""
test

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import json

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.event import RotateEvent
from pymysqlreplication.row_event import RowsEvent
from pymysqlreplication.row_event import DeleteRowsEvent
from pymysqlreplication.row_event import UpdateRowsEvent
from pymysqlreplication.row_event import WriteRowsEvent


def test():

    connection_settings = {
        'host': 'chocon-cluster-dev.cluster-csiquhqyczzd.ap-northeast-1.rds.amazonaws.com',
        'port': 6303,
        'user': 'conan',
        'passwd': 'ShAwpgSxX3JB3ZRy',
    }

    stream = BinLogStreamReader(
        connection_settings,
        server_id=100,
        blocking=True,
        resume_stream=True,
        log_file='mysql-bin-changelog.000003',
        log_pos=1324
    )

    for event in stream:
        event.dump()

        if isinstance(event, RowsEvent):
            print event.rows
            print event.schema
            print event.table
            # print event.columns
            print event.number_of_columns
            print event.primary_key


if __name__ == '__main__':
    test()
