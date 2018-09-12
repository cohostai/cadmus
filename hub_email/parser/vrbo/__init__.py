#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals
from ..base import CascadingEmailParser

from .message import MessageEmailParser

VRBO_EMAIL_PARSER = CascadingEmailParser([
    MessageEmailParser(),
])
