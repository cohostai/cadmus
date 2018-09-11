#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from collections import defaultdict


class RowProcessor(object):

    def process(self, schema, table, row):
        raise NotImplementedError

    @staticmethod
    def _get_table_full_name(schema, table):
        return "{schema}.{table}".format(
            schema=schema, table=table)


class DefaultRowProcessor(RowProcessor):

    def process(self, schema, table, row):
        if "values" in row:
            doc = row["values"]
        elif "after_values" in row:
            doc = row["after_values"]
        else:
            table_full_name = self._get_table_full_name(schema, table)
            raise Exception("Invalid row for table %s: %s" % (
                table_full_name, row))
        return doc


class CascadingRowProcessor(RowProcessor):

    def __init__(self):
        self._default_processor = DefaultRowProcessor()
        self._table_to_processor = defaultdict(lambda: self._default_processor)

    def process(self, schema, table, row):
        table_full_name = self._get_table_full_name(schema, table)
        processor = self._table_to_processor[table_full_name]
        return processor.process(schema, table, row)

    def register(self, schema, table, processor):
        """

        Args:
            schema:
            table:
            processor:

        Returns:

        """
        table_full_name = self._get_table_full_name(schema, table)
        self._table_to_processor[table_full_name] = processor
