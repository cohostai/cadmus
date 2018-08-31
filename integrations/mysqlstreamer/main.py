#!/usr/bin/env python
# encoding: utf-8
"""
main

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import signal
import time
import sys
import os

from integrations.mysqlstreamer import config
from integrations.mysqlstreamer.app import App
from integrations.mysqlstreamer.utils import log

logger = log.get_logger(__name__)

app = App(config)


def terminate(signum, stack):
    app.stop()

signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGINT, terminate)


if __name__ == '__main__':
    app.start()
    logger.info('Stopped. See ya again.')
