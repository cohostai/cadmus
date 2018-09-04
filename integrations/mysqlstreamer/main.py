#!/usr/bin/env python
# encoding: utf-8
"""
main

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

import signal
import time
import subprocess
import os

from six import text_type

from integrations.mysqlstreamer import config
from integrations.mysqlstreamer.app import App
from integrations.mysqlstreamer.utils import log

logger = log.get_logger(__name__)

app = App(config)


def terminate(signum, stack):
    logger.info('App is terminating...')
    app.stop()
    subprocess.call(['kill',  '-15', text_type(os.getpid())])


def wait_for_termination():
    while not app.should_stop():
        time.sleep(5)


signal.signal(signal.SIGINT, terminate)


if __name__ == '__main__':
    app.start()
    wait_for_termination()
    logger.info('Stopped. See ya again.')
