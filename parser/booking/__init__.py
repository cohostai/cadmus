#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from ..base import CascadingEmailParser
from .message import MessageParser

BOOKING_EMAIL_PARSER = CascadingEmailParser([
    MessageParser(),
])
