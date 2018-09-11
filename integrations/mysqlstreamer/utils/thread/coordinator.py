#!/usr/bin/env python
# encoding: utf-8
"""
coordinator

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals


class Coordinator(object):

    def __init__(self):
        self._stop = False

    def should_stop(self):
        return self._stop

    def reset(self):
        self._stop = False

    def stop(self):
        self._stop = True
