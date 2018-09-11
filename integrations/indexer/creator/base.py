#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from elasticsearch import Elasticsearch

from ..utils import log

logger = log.get_logger(__name__)


class BaseIndexCreator(object):

    def create(self):
        raise NotImplementedError


class CompositeIndexCreator(BaseIndexCreator):

    def __init__(self, creators):
        self._creators = creators

    def create(self):
        for creator in self._creators:
            creator.create()


class IndexCreator(BaseIndexCreator):

    def __init__(self, client, index_name,
                 settings=None, mappings=None, aliases=None, **kwargs):

        self._client = client  # type: Elasticsearch
        self._index_name = index_name
        self._settings = settings
        self._mappings = mappings
        self._aliases = aliases

    def create(self):
        if self._client.indices.exists(index=self._index_name):
            self._maybe_update_mappings()
            return

        return self._create()

    def _maybe_update_mappings(self):
        # mappings = self._client.indices.get_mapping(
        #     index=self._index_name,
        #     doc_type='_doc',
        # )
        #
        # mappings = mappings[self._index_name]['mappings']['_doc']
        #
        # logger.warn('MAPPINGS: %s', mappings)
        # logger.warn('MAPPINGS: %s', self._mappings['_doc'])
        #
        # if mappings != self._mappings:

        result = self._client.indices.put_mapping(
            index=self._index_name,
            doc_type='_doc',
            body=self._mappings['_doc']
        )

    def _create(self):
        body = self._get_body()
        result = self._client.indices.create(
            index=self._index_name,
            body=body
        )

    def _get_body(self):
        body = {}
        if self._settings:
            body["settings"] = self._settings
        if self._mappings:
            body["mappings"] = self._mappings
        if self._aliases:
            body["aliases"] = self._aliases

        return body
