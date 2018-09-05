#!/usr/bin/env python
# encoding: utf-8
"""
users

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from .base import DefaultRowProcessor


class UserRowProcessor(DefaultRowProcessor):

    def process(self, schema, table, row):
        doc = super(UserRowProcessor, self).process(schema, table, row)
        return doc
