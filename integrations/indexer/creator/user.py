#!/usr/bin/env python
# encoding: utf-8
"""
users

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import, unicode_literals

from .base import IndexCreator

INDEX_NAME = 'chocon_users_v1'

INDEX_SETTINGS = {
    "index": {
        "number_of_shards": 5,
        "number_of_replicas": 1
    }
}

INDEX_MAPPINGS = {
    "_doc": {
        "properties": {
            "id": {
                "type": "integer"
            },
            "first_name": {
                "type": "text"
            },
            "last_name": {
                "type": "text"
            },
            "about": {
                "type": "text"
            },
            "email": {
                "type": "keyword",
            },
            "phone": {
                "type": "keyword",
            },
            "country_code": {
                "type": "keyword",
            },
            "location_geopoint": {
                "type": "geo_point"
            },
            "created_at": {
                "type": "date"
            },
            "modified_at": {
                "type": "date"
            },
            "deleted_at": {
                "type": "date"
            },
            "status": {
                "type": "keyword"
            },
            "score": {
                "type": "integer"
            },
            "identity_verified": {
                "type": "boolean"
            },
            "role": {
                "type": "keyword",
            },
            "languages": {
                "type": "text"
            },
            "slack_thread_id": {
                "type": "keyword"
            },
            "avatar": {
                "type": "keyword",
            }
        }
    }
}

INDEX_ALIASES = {
    "chocon_users": {}
}


class UsersIndexCreator(IndexCreator):

    def __init__(self, client):
        super(UsersIndexCreator, self).__init__(
            client,
            INDEX_NAME,
            INDEX_SETTINGS,
            INDEX_MAPPINGS,
            INDEX_ALIASES
        )
